/// Oracle contract implementation using ledger keys for storing each price.
/// This implementation is a rework of the previous implementation that used
/// maps for storing prices (see contract_map.rs). The main difference is that
/// this implementation stores each price in its dedicated ledger key in temporary
/// storage, which allows for more efficient storage and execution due to the
/// minimal amount of CPU instructions required to add/retrieve prices, as well as
/// removes the scalability issues we had in the previous implementation.
use soroban_sdk::{contract, contractimpl, Address, BytesN, Env, Vec};

use crate::constants::{ADMIN, ASSETS, BASE_ASSET, DECIMALS, LAST_TIMESTAMP, RESOLUTION, SOURCES};
use crate::types::{Asset, InternalAsset, InternalPrice, PriceData};
use crate::utils::{get_asset_as_u32, to_price_data_key};

pub trait LightOracleTrait {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32);
    fn bump_instance(env: Env, ledgers_to_live: u32);
    fn write_admin(env: Env, id: Address);
    fn read_admin(env: Env) -> Option<Address>;
    fn sources(env: Env) -> Vec<u32>;
    fn prices_by_source(
        env: Env,
        source: u32,
        asset: Asset,
        records: u32,
    ) -> Option<Vec<PriceData>>;
    fn price_by_source(env: Env, source: u32, asset: Asset, timestamp: u64) -> Option<PriceData>;
    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData>;
    fn add_assets(env: Env, assets: Vec<InternalAsset>);
    fn remove_assets(env: Env, assets: Vec<InternalAsset>);
    fn get_internal_assets(env: Env) -> Vec<InternalAsset>;
    fn add_prices(env: Env, prices: Vec<InternalPrice>);
    fn update_contract(env: Env, wasm_hash: BytesN<32>);

    // SEP-40
    fn base(env: Env) -> Asset;
    fn assets(env: Env) -> Vec<Asset>;
    fn decimals(env: Env) -> u32;
    fn resolution(env: Env) -> u32;
    fn price(env: Env, asset: Asset, timestamp: u64) -> Option<PriceData>;
    fn prices(env: Env, asset: Asset, records: u32) -> Option<Vec<PriceData>>;
    fn lastprice(env: Env, asset: Asset) -> Option<PriceData>;
}

#[contract]
pub struct LightOracle;

#[contractimpl]
impl LightOracleTrait for LightOracle {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32) {
        let existing_admin: Option<Address> = env.storage().instance().get(&ADMIN);
        if existing_admin.is_some() {
            panic!("already initialized");
        }

        env.storage().instance().set(&ADMIN, &admin);
        env.storage()
            .instance()
            .set(&SOURCES, &Vec::<u32>::new(&env));
        env.storage()
            .instance()
            .set(&ASSETS, &Vec::<Asset>::new(&env));
        env.storage().instance().set(&BASE_ASSET, &base);
        env.storage().instance().set(&DECIMALS, &decimals);
        env.storage().instance().set(&RESOLUTION, &resolution);
        env.storage().instance().set(&LAST_TIMESTAMP, &0);
    }

    fn bump_instance(env: Env, ledgers_to_live: u32) {
        env.storage()
            .instance()
            .extend_ttl(ledgers_to_live, ledgers_to_live);
    }

    fn write_admin(env: Env, new_admin: Address) {
        panic_if_not_admin(&env);
        env.storage().instance().set(&ADMIN, &new_admin);
    }

    fn read_admin(env: Env) -> Option<Address> {
        return env.storage().instance().get(&ADMIN);
    }

    fn sources(env: Env) -> Vec<u32> {
        return env.storage().instance().get(&SOURCES).unwrap();
    }

    fn price_by_source(env: Env, source: u32, asset: Asset, timestamp: u64) -> Option<PriceData> {
        return price_by_source(&env, source, asset, timestamp);
    }

    fn prices_by_source(
        env: Env,
        source: u32,
        asset: Asset,
        records: u32,
    ) -> Option<Vec<PriceData>> {
        let mut timestamp: u64 = env.storage().instance().get(&LAST_TIMESTAMP).unwrap();
        if timestamp == 0 {
            return None;
        }
        let resolution: u64 = env.storage().instance().get(&RESOLUTION).unwrap();
        let mut prices = Vec::new(&env);

        let mut records = records;
        if records > 20 {
            records = 20;
        }

        for _ in 0..records {
            let price = price_by_source(&env, source, asset.clone(), timestamp);
            if price.is_none() {
                continue;
            }
            prices.push_back(price.unwrap());
            if timestamp < resolution {
                break;
            }
            timestamp -= resolution;
        }

        if prices.len() == 0 {
            return None;
        }

        Some(prices)
    }

    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData> {
        let timestamp: u64 = env.storage().instance().get(&LAST_TIMESTAMP).unwrap();
        return LightOracle::price_by_source(env, source, asset, timestamp);
    }

    fn add_assets(env: Env, assets: Vec<InternalAsset>) {
        panic_if_not_admin(&env);
        for asset in assets {
            match asset.asset {
                Asset::Stellar(address) => {
                    env.storage().instance().set(&address, &asset.asset_u32);
                }
                Asset::Other(symbol) => {
                    env.storage().instance().set(&symbol, &asset.asset_u32);
                }
            };
        }
    }

    fn remove_assets(env: Env, assets: Vec<InternalAsset>) {
        panic_if_not_admin(&env);
        for asset in assets {
            env.storage().instance().remove(&asset.asset);
        }
    }

    fn get_internal_assets(env: Env) -> Vec<InternalAsset> {
        let mut internal_assets = Vec::<InternalAsset>::new(&env);
        let assets: Vec<Asset> = env.storage().instance().get(&ASSETS).unwrap();
        for asset in assets {
            let asset_u32 = get_asset_as_u32(&env, asset.clone()).unwrap();
            internal_assets.push_back(InternalAsset { asset, asset_u32 });
        }
        return internal_assets;
    }

    fn add_prices(env: Env, prices: Vec<InternalPrice>) {
        panic_if_not_admin(&env);
        write_prices(&env, prices);
    }

    fn update_contract(env: Env, wasm_hash: BytesN<32>) {
        panic_if_not_admin(&env);
        env.deployer().update_current_contract_wasm(wasm_hash);
    }

    fn base(env: Env) -> Asset {
        return env.storage().instance().get(&BASE_ASSET).unwrap();
    }

    fn assets(env: Env) -> Vec<Asset> {
        return env.storage().instance().get(&ASSETS).unwrap();
    }

    fn decimals(env: Env) -> u32 {
        return env.storage().instance().get(&DECIMALS).unwrap();
    }

    fn resolution(env: Env) -> u32 {
        return env.storage().instance().get(&RESOLUTION).unwrap();
    }

    fn price(env: Env, asset: Asset, timestamp: u64) -> Option<PriceData> {
        return LightOracle::price_by_source(env, 0, asset, timestamp);
    }

    fn prices(env: Env, asset: Asset, records: u32) -> Option<Vec<PriceData>> {
        return LightOracle::prices_by_source(env, 0, asset, records);
    }

    fn lastprice(env: Env, asset: Asset) -> Option<PriceData> {
        return LightOracle::lastprice_by_source(env, 0, asset);
    }
}

fn panic_if_not_admin(env: &Env) {
    let admin: Option<Address> = env.storage().instance().get(&ADMIN);
    return admin.unwrap().require_auth();
}

fn write_prices(env: &Env, prices: Vec<InternalPrice>) {
    let mut assets = Vec::<Asset>::new(&env);
    let mut sources = Vec::<u32>::new(&env);
    for price in prices {
        let asset_u32 = get_asset_as_u32(env, price.asset.clone());
        if asset_u32.is_none() {
            panic!("asset not found");
        }
        let key = to_price_data_key(price.source, asset_u32.unwrap(), price.timestamp);
        assets.push_back(price.asset.clone());
        sources.push_back(price.source);
        env.storage().temporary().set(&key, &price);
    }
    let mut unique_assets = Vec::<Asset>::new(&env);
    let mut unique_sources = Vec::<u32>::new(&env);
    for asset in assets {
        if !unique_assets.contains(&asset) {
            unique_assets.push_back(asset);
        }
    }
    for source in sources {
        if !unique_sources.contains(&source) {
            unique_sources.push_back(source);
        }
    }
    env.storage().instance().set(&ASSETS, &unique_assets);
    env.storage().instance().set(&SOURCES, &unique_sources);
}

fn price_by_source(env: &Env, source: u32, asset: Asset, timestamp: u64) -> Option<PriceData> {
    let asset_u32 = get_asset_as_u32(env, asset).unwrap();
    let key = to_price_data_key(source, asset_u32, timestamp);
    return env.storage().temporary().get(&key);
}
