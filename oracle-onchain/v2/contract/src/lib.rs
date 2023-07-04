#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, Env, Map, Set, Symbol, Vec};

#[derive(Clone, Copy)]
#[contracttype]
#[repr(u32)]
pub enum DataKey {
    Base = 0,
    Decimals = 1,
    Resolution = 2,
    Admin = 3,
    Prices = 4,
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub enum Asset {
    Stellar(Address),
    Other(Symbol),
}

#[derive(Clone, Copy, Debug)]
#[contracttype]
pub struct PriceData {
    pub price: i128,
    pub timestamp: u64,
}

impl PriceData {
    pub fn new(price: i128, timestamp: u64) -> Self {
        Self { price, timestamp }
    }
}

pub struct Oracle;

fn get_admin(env: &Env) -> Address {
    return env.storage().get_unchecked(&DataKey::Admin).unwrap();
}

fn is_u32_in_vec(n: u32, vec: &Vec<u32>) -> bool {
    for item in vec.iter_unchecked() {
        if item == n {
            return true;
        }
    }
    return false;
}

fn is_asset_in_vec(asset: Asset, vec: &Vec<Asset>) -> bool {
    for item in vec.iter_unchecked() {
        if item == asset {
            return true;
        }
    }
    return false;
}

pub trait OracleTrait {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32);

    fn admin(env: Env) -> Address;

    /// Return list of all price sources
    fn sources(env: Env) -> Vec<u32>;

    /// Return list of prices from a given source
    fn prices_by_source(
        env: Env,
        source: u32,
        asset: Asset,
        start_timestamp: u64,
        end_timestamp: u64,
    ) -> Vec<PriceData>;

    /// Get source=0 last N price records
    fn lastprices(env: Env, asset: Asset, records: u32) -> Vec<PriceData>;

    /// Get source=<source> last N price records
    fn lastprices_by_source(env: Env, source: u32, asset: Asset, records: u32) -> Vec<PriceData>;

    /// Get source=<source> last price record
    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData>;

    /// Add a price record
    fn add_price(env: Env, source: u32, asset: Asset, price: i128);

    //TODO add bulk prices

    /// Remove prices matching the given conditions.
    /// Parameters:
    ///   sources: a list of sources to match when removing prices. If this is an
    ///            empty list, all sources are be matched.
    ///   assets: a list of assets to match when removing prices. If this is an
    ///            empty list, all assets are matched.
    ///   start_timestamp: prices with timestamp higher than or equal to
    ///            start_timestamp will be matched.
    ///   end_timestamp: prices with timestamp lower than or equal to
    ///            end_timestamp will be matched.
    /// Examples:
    ///   To remove all prices from source=1:
    ///     remove_prices(env, &Vec::<Asset>::from_array(&env, [1]), &Vec::<Asset>::new(&env), None, None);
    ///
    ///   To remove all prices of asset `AssetB` from all sources:
    ///     remove_prices(env, &Vec::<u32>::new(&env), &Vec::<Asset>::from_array(&env, [AssetB]), None, None);
    ///
    ///   To remove all prices of asset `AssetB` from source=1:
    ///     remove_prices(env, &Vec::<u32>::from_array(&env, [1]), &Vec::<Asset>::from_array(&env, [AssetB]), None, None);
    ///
    ///   To remove all prices with timestamp higher than `my_timestamp`:
    ///     remove_prices(env, &Vec::<u32>::new(&env), &Vec::<Asset>::new(&env), &my_timestamp, None);
    fn remove_prices(
        env: Env,
        sources: Vec<u32>,
        assets: Vec<Asset>,
        start_timestamp: Option<u64>,
        end_timestamp: Option<u64>,
    );

    ///
    /// SEP-40 functions
    ///

    /// Return the base asset the price is reported in.
    fn base(env: Env) -> Asset;

    /// Return all assets quoted by the price feed.
    fn assets(env: Env) -> Vec<Asset>;

    /// Return the number of decimals for all assets quoted by the oracle.
    fn decimals(env: Env) -> u32;

    /// Return default tick period timeframe (in seconds).
    fn resolution(env: Env) -> u32;

    /// Get source=0 prices (in base asset) contained in the provided timestamp
    ///  range, ordered by oldest to newest.
    /// Both timestamps are inclusive, meaning if there's a price exactly at
    ///  `start_timestamp`, it will be included. Same for `end_timestamp`.
    fn prices(env: Env, asset: Asset, start_timestamp: u64, end_timestamp: u64) -> Vec<PriceData>;

    /// Get source=0 latest price in base asset
    fn lastprice(env: Env, asset: Asset) -> Option<PriceData>;
}

#[contractimpl]
impl OracleTrait for Oracle {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32) {
        // if an admin is already set, we require admin authentication
        let admin_option = env.storage().get(&DataKey::Admin);
        match admin_option {
            Some(admin_result) => {
                let admin: Address = admin_result.unwrap();
                admin.require_auth();
            }
            None => {}
        }

        let storage = env.storage();
        storage.set(&DataKey::Base, &base);
        storage.set(&DataKey::Decimals, &decimals);
        storage.set(&DataKey::Resolution, &resolution);
        storage.set(
            &DataKey::Prices,
            &Map::<u32, Map<Asset, Vec<PriceData>>>::new(&env),
        );
        storage.set(&DataKey::Admin, &admin);
    }

    fn base(env: Env) -> Asset {
        return env.storage().get_unchecked(&DataKey::Base).unwrap();
    }

    fn admin(env: Env) -> Address {
        return env.storage().get_unchecked(&DataKey::Admin).unwrap();
    }

    fn assets(env: Env) -> Vec<Asset> {
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            env.storage().get_unchecked(&DataKey::Prices).unwrap();
        let mut asset_set = Set::<Asset>::new(&env);
        for (_, asset_map) in source_map.iter_unchecked() {
            for (asset, _) in asset_map.iter_unchecked() {
                asset_set.insert(asset);
            }
        }
        return asset_set.to_vec();
    }

    fn sources(env: Env) -> Vec<u32> {
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            env.storage().get_unchecked(&DataKey::Prices).unwrap();
        return source_map.keys();
    }

    fn decimals(env: Env) -> u32 {
        return env.storage().get_unchecked(&DataKey::Decimals).unwrap();
    }

    fn resolution(env: Env) -> u32 {
        return env.storage().get_unchecked(&DataKey::Resolution).unwrap();
    }

    fn prices(env: Env, asset: Asset, start_timestamp: u64, end_timestamp: u64) -> Vec<PriceData> {
        return Oracle::prices_by_source(env, 0, asset, start_timestamp, end_timestamp);
    }

    fn prices_by_source(
        env: Env,
        source: u32,
        asset: Asset,
        start_timestamp: u64,
        end_timestamp: u64,
    ) -> Vec<PriceData> {
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            env.storage().get_unchecked(&DataKey::Prices).unwrap();
        let mut prices_within_range: Vec<PriceData> = Vec::<PriceData>::new(&env);
        let asset_map_option = source_map.get(source);
        match asset_map_option {
            Some(asset_map_result) => {
                let asset_map = asset_map_result.unwrap();
                let prices_vec_option = asset_map.get(asset.clone());
                match prices_vec_option {
                    Some(prices_vec_result) => {
                        let prices_vec = prices_vec_result.unwrap();
                        for price_data in prices_vec.iter_unchecked() {
                            if price_data.timestamp >= start_timestamp
                                && price_data.timestamp <= end_timestamp
                            {
                                prices_within_range.push_back(price_data)
                            }
                        }
                    }
                    None => return prices_within_range,
                }
            }
            None => return prices_within_range,
        }
        return prices_within_range;
    }

    fn lastprices(env: Env, asset: Asset, records: u32) -> Vec<PriceData> {
        return Oracle::lastprices_by_source(env, 0, asset, records);
    }

    fn lastprices_by_source(env: Env, source: u32, asset: Asset, records: u32) -> Vec<PriceData> {
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            env.storage().get_unchecked(&DataKey::Prices).unwrap();
        let mut prices_within_range: Vec<PriceData> = Vec::<PriceData>::new(&env);
        let asset_map_option = source_map.get(source);
        match asset_map_option {
            Some(asset_map_result) => {
                let asset_map = asset_map_result.unwrap();
                let prices_vec_option = asset_map.get(asset.clone());
                match prices_vec_option {
                    Some(prices_vec_result) => {
                        let prices_vec = prices_vec_result.unwrap();
                        let starting_index = prices_vec.len().checked_sub(records).unwrap_or(0);
                        for (index_usize, price_data) in prices_vec.iter_unchecked().enumerate() {
                            let index: u32 = index_usize.try_into().unwrap();
                            if index < starting_index {
                                continue;
                            }
                            prices_within_range.push_back(price_data)
                        }
                    }
                    None => return prices_within_range,
                }
            }
            None => return prices_within_range,
        }
        return prices_within_range;
    }

    fn lastprice(env: Env, asset: Asset) -> Option<PriceData> {
        return Oracle::lastprice_by_source(env, 0, asset);
    }

    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData> {
        let prices = Oracle::lastprices_by_source(env, source, asset, 1);
        for price_data in prices.iter_unchecked() {
            return Some(price_data);
        }
        return None;
    }

    fn add_price(env: Env, source: u32, asset: Asset, price: i128) {
        get_admin(&env).require_auth();
        let storage = env.storage();
        let mut source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            storage.get_unchecked(&DataKey::Prices).unwrap();
        let asset_map_option = source_map.get(source);
        let mut asset_map;
        match asset_map_option {
            Some(asset_map_result) => {
                asset_map = asset_map_result.unwrap();
            }
            None => {
                asset_map = Map::<Asset, Vec<PriceData>>::new(&env);
            }
        }
        let price_data_vec_option = asset_map.get(asset.clone());
        let mut price_data_vec;
        match price_data_vec_option {
            Some(price_data_vec_result) => {
                price_data_vec = price_data_vec_result.unwrap();
            }
            None => {
                price_data_vec = Vec::<PriceData>::new(&env);
            }
        }
        let timestamp = env.ledger().timestamp();
        if price_data_vec.len() >= 10 {
            price_data_vec.pop_front();
        }
        price_data_vec.push_back(PriceData::new(price, timestamp));
        asset_map.set(asset.clone(), price_data_vec);
        source_map.set(source, asset_map.clone());
        storage.set(&DataKey::Prices, &source_map);
    }

    fn remove_prices(
        env: Env,
        sources: Vec<u32>,
        assets: Vec<Asset>,
        start_timestamp: Option<u64>,
        end_timestamp: Option<u64>,
    ) {
        get_admin(&env).require_auth();
        let storage = env.storage();
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            storage.get_unchecked(&DataKey::Prices).unwrap();
        let mut new_source_map = Map::<u32, Map<Asset, Vec<PriceData>>>::new(&env);
        let sources_len = sources.len();
        let assets_len = assets.len();
        for (source, asset_map) in source_map.iter_unchecked() {
            if sources_len > 0 && !is_u32_in_vec(source, &sources) {
                new_source_map.set(source, asset_map);
                continue;
            }
            let mut new_asset_map = Map::<Asset, Vec<PriceData>>::new(&env);
            for (asset, price_data_vec) in asset_map.iter_unchecked() {
                if assets_len > 0 && !is_asset_in_vec(asset.clone(), &assets) {
                    new_asset_map.set(asset.clone(), price_data_vec);
                    continue;
                }
                let mut new_price_data_vec = Vec::<PriceData>::new(&env);
                for price_data in price_data_vec.iter_unchecked() {
                    match start_timestamp {
                        Some(t) => {
                            if t < price_data.timestamp {
                                new_price_data_vec.push_back(price_data);
                                continue;
                            }
                        }
                        None => {}
                    }
                    match end_timestamp {
                        Some(t) => {
                            if t > price_data.timestamp {
                                new_price_data_vec.push_back(price_data);
                                continue;
                            }
                        }
                        None => {}
                    }
                }
                if new_price_data_vec.len() > 0 {
                    new_asset_map.set(asset.clone(), new_price_data_vec)
                }
            }
            if new_asset_map.keys().len() > 0 {
                new_source_map.set(source, new_asset_map);
            }
        }
        storage.set(&DataKey::Prices, &new_source_map);
    }
}

mod test;
