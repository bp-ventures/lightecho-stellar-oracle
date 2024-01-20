/// Oracle contract implementation using ledger keys for storing each price.
/// This implementation is a rework of the previous implementation that used
/// maps for storing prices (see contract_map.rs). The main difference is that
/// this implementation stores each price in its dedicated ledger key in temporary
/// storage, which allows for more efficient storage and execution due to the
/// minimal amount of CPU instructions required to add/retrieve prices, as well as
/// removes the scalability issues we had in the previous implementation.
use soroban_sdk::{contract, contractimpl, Address, BytesN, Env, Vec};

use crate::constants::{
    ADMIN, ASSETS, BASE_ASSET, DECIMALS, LAST_TIMESTAMP, RESOLUTION, SOURCES, TEMPORARY_KEY_TTL,
};
use crate::types::{Asset, InternalAsset, InternalPrice, PriceData};
use crate::utils::{get_asset_as_u32, set_asset_as_u32, to_price_data_key};

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
    fn get_internal_assets(env: Env) -> Vec<InternalAsset>;
    fn add_prices(env: Env, prices: Vec<InternalPrice>);
    fn add_prices_light(env: Env, prices: Vec<InternalPrice>);
    fn update_contract(env: Env, wasm_hash: BytesN<32>);
    fn get_asset_as_u32(env: Env, asset: Asset) -> Option<u32>;
    fn remove_assets(env: Env, assets: Vec<Asset>);
    fn remove_sources(env: Env, sources: Vec<u32>);

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
        let storage_admin: Option<Address> = env.storage().instance().get(&ADMIN);
        if storage_admin.is_some() {
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
        return match env.storage().instance().get(&SOURCES) {
            Some(sources) => sources,
            None => panic!("SOURCES is not initialized"),
        };
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
        let mut timestamp: u64 = match env.storage().instance().get(&LAST_TIMESTAMP) {
            Some(timestamp) => timestamp,
            None => panic!("LAST_TIMESTAMP is not initialized"),
        };
        if timestamp == 0 {
            return None;
        }
        let resolution_u32: u32 = match env.storage().instance().get(&RESOLUTION) {
            Some(resolution) => resolution,
            None => panic!("RESOLUTION is not initialized"),
        };
        let resolution_u64 = resolution_u32 as u64;
        let mut prices = Vec::new(&env);

        let mut records = records;
        if records > 20 {
            records = 20;
        }

        for _ in 0..records {
            let price = match price_by_source(&env, source, asset.clone(), timestamp) {
                Some(price) => price,
                None => {
                    if timestamp < resolution_u64 {
                        break;
                    }
                    timestamp -= resolution_u64;
                    continue;
                }
            };
            prices.push_back(price);
            if timestamp < resolution_u64 {
                break;
            }
            timestamp -= resolution_u64;
        }

        if prices.len() == 0 {
            return None;
        }

        Some(prices)
    }

    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData> {
        let timestamp: u64 = match env.storage().instance().get(&LAST_TIMESTAMP) {
            Some(timestamp) => timestamp,
            None => panic!("LAST_TIMESTAMP is not initialized"),
        };
        return LightOracle::price_by_source(env, source, asset, timestamp);
    }

    /// Returns a list of InternalAsset structs that contain the asset and its
    /// u32 representation.
    fn get_internal_assets(env: Env) -> Vec<InternalAsset> {
        let mut internal_assets = Vec::<InternalAsset>::new(&env);
        let assets: Vec<Asset> = match env.storage().instance().get(&ASSETS) {
            Some(assets) => assets,
            None => panic!("ASSETS is not initialized"),
        };
        for asset in assets {
            let asset_u32 = match get_asset_as_u32(&env, asset.clone()) {
                Some(asset_u32) => asset_u32,
                None => panic!("asset not found"),
            };
            internal_assets.push_back(InternalAsset { asset, asset_u32 });
        }
        return internal_assets;
    }

    /// A utility function for getting the u32 representation of an asset that
    /// is registered in the storage.
    fn get_asset_as_u32(env: Env, asset: Asset) -> Option<u32> {
        return get_asset_as_u32(&env, asset);
    }

    /// Removes assets from the contract.
    /// This only removes assets from the ASSETS storage key. It doesn't remove
    /// price entries from the temporary storage.
    fn remove_assets(env: Env, assets: Vec<Asset>) {
        panic_if_not_admin(&env);
        let storage_assets: Vec<Asset> = match env.storage().instance().get(&ASSETS) {
            Some(assets) => assets,
            None => panic!("ASSETS is not initialized"),
        };
        let mut new_assets = Vec::<Asset>::new(&env);
        for asset in storage_assets {
            if !assets.contains(&asset) {
                new_assets.push_back(asset);
            }
        }
        env.storage().instance().set(&ASSETS, &new_assets);
    }

    /// Removes SOURCES from the contract.
    /// This only removes SOURCES from the SOURCES storage key. It doesn't remove
    /// price entries from the temporary storage.
    fn remove_sources(env: Env, sources: Vec<u32>) {
        panic_if_not_admin(&env);
        let storage_sources: Vec<u32> = match env.storage().instance().get(&SOURCES) {
            Some(sources) => sources,
            None => panic!("SOURCES is not initialized"),
        };
        let mut new_sources = Vec::<u32>::new(&env);
        for source in storage_sources {
            if !sources.contains(&source) {
                new_sources.push_back(source);
            }
        }
        env.storage().instance().set(&SOURCES, &new_sources);
    }

    /// Adds prices to the contract.
    /// Sources and assets get automatically registered in the storage. Which
    /// is handy but not always necessary because once assets and sources are
    /// registered, they don't need to be registered again.
    /// For a more lightweight version of this function, see add_prices_light.
    fn add_prices(env: Env, prices: Vec<InternalPrice>) {
        panic_if_not_admin(&env);
        let mut storage_assets: Vec<Asset> = match env.storage().instance().get(&ASSETS) {
            Some(assets) => assets,
            None => panic!("ASSETS is not initialized"),
        };
        let mut storage_sources: Vec<u32> = match env.storage().instance().get(&SOURCES) {
            Some(sources) => sources,
            None => panic!("SOURCES is not initialized"),
        };
        let mut highest_timestamp = 0;
        for price in prices {
            if !storage_assets.contains(&price.asset) {
                storage_assets.push_back(price.asset.clone());
                set_asset_as_u32(&env, price.asset.clone(), price.asset_u32);
            }
            if !storage_sources.contains(&price.source) {
                storage_sources.push_back(price.source);
            }

            let key = to_price_data_key(price.source, price.asset_u32, price.timestamp);
            env.storage()
                .temporary()
                .set(&key, &PriceData::new(price.price, price.timestamp));
            env.storage()
                .temporary()
                .extend_ttl(&key, TEMPORARY_KEY_TTL, TEMPORARY_KEY_TTL);
            if price.timestamp > highest_timestamp {
                highest_timestamp = price.timestamp;
            }
        }

        env.storage().instance().set(&ASSETS, &storage_assets);
        env.storage().instance().set(&SOURCES, &storage_sources);
        env.storage()
            .instance()
            .set(&LAST_TIMESTAMP, &highest_timestamp);
    }

    /// A more lightweight version of add_prices that does not update the
    /// ASSETS and SOURCES storage keys. This is useful for adding prices
    /// for existing assets and sources without spending unnecessary fees.
    fn add_prices_light(env: Env, prices: Vec<InternalPrice>) {
        panic_if_not_admin(&env);
        let mut highest_timestamp = 0;
        for price in prices {
            let key = to_price_data_key(price.source, price.asset_u32, price.timestamp);
            env.storage()
                .temporary()
                .set(&key, &PriceData::new(price.price, price.timestamp));
            env.storage()
                .temporary()
                .extend_ttl(&key, TEMPORARY_KEY_TTL, TEMPORARY_KEY_TTL);
            if price.timestamp > highest_timestamp {
                highest_timestamp = price.timestamp;
            }
        }

        env.storage()
            .instance()
            .set(&LAST_TIMESTAMP, &highest_timestamp);
    }

    fn update_contract(env: Env, wasm_hash: BytesN<32>) {
        panic_if_not_admin(&env);
        env.deployer().update_current_contract_wasm(wasm_hash);
    }

    fn base(env: Env) -> Asset {
        return match env.storage().instance().get(&BASE_ASSET) {
            Some(base) => base,
            None => panic!("BASE_ASSET is not initialized"),
        };
    }

    fn assets(env: Env) -> Vec<Asset> {
        return match env.storage().instance().get(&ASSETS) {
            Some(assets) => assets,
            None => panic!("ASSETS is not initialized"),
        };
    }

    fn decimals(env: Env) -> u32 {
        return match env.storage().instance().get(&DECIMALS) {
            Some(decimals) => decimals,
            None => panic!("DECIMALS is not initialized"),
        };
    }

    fn resolution(env: Env) -> u32 {
        return match env.storage().instance().get(&RESOLUTION) {
            Some(resolution) => resolution,
            None => panic!("RESOLUTION is not initialized"),
        };
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
    let admin: Address = match env.storage().instance().get(&ADMIN) {
        Some(admin) => admin,
        None => panic!("ADMIN is not initialized"),
    };
    return admin.require_auth();
}

fn price_by_source(env: &Env, source: u32, asset: Asset, timestamp: u64) -> Option<PriceData> {
    let asset_u32 = match get_asset_as_u32(env, asset) {
        Some(asset_u32) => asset_u32,
        None => panic!("asset not found"),
    };
    let key = to_price_data_key(source, asset_u32, timestamp);
    return env.storage().temporary().get(&key);
}
