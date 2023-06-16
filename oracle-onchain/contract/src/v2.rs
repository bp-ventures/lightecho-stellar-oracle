use soroban_sdk::{contractimpl, contracttype, Address, Env, Map, Symbol, Vec};

#[derive(Clone, Copy)]
#[contracttype]
#[repr(u32)]
pub enum DataKey {
    Base = 0,
    Decimals = 1,
    Resolution = 2,
    Assets = 3,
    Prices = 4,
    Admin = 5,
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub enum Asset {
    Stellar(Address),
    Other(Symbol),
}

#[derive(Clone, Copy)]
#[contracttype]
pub struct PriceData {
    price: i128,
    timestamp: u64,
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

pub trait OracleTrait {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32);

    /// Return the base asset the price is reported in.
    fn base(env: Env) -> Asset;

    /// Return all assets quoted by the price feed.
    fn assets(env: Env) -> Vec<Asset>;

    /// Return all sources
    //fn sources(env: Env) -> Vec<u32>;

    /// Return the number of decimals for all assets quoted by the oracle.
    fn decimals(env: Env) -> u32;

    /// Return default tick period timeframe (in seconds).
    fn resolution(env: Env) -> u32;

    /// Get source=0 prices (in base asset) contained in the provided timestamp
    ///  range, ordered by oldest to newest.
    /// Both timestamps are inclusive, meaning if there's a price exactly at
    ///  `start_timestamp`, it will be included. Same for `end_timestamp`.
    fn prices(env: Env, asset: Asset, start_timestamp: u64, end_timestamp: u64) -> Vec<PriceData>;

    fn prices_by_source(
        env: Env,
        source: u32,
        asset: Asset,
        start_timestamp: u64,
        end_timestamp: u64,
    ) -> Vec<PriceData>;

    /// Get source=0 last N price records
    fn lastprices(env: Env, asset: Asset, records: u32) -> Vec<PriceData>;

    fn lastprices_by_source(env: Env, source: u32, asset: Asset, records: u32) -> Vec<PriceData>;

    /// Get source=0 latest price in base asset
    fn lastprice(env: Env, asset: Asset) -> Option<PriceData>;

    fn lastprice_by_source(env: Env, source: u32, asset: Asset) -> Option<PriceData>;

    fn add_price(env: Env, source: u32, asset: Asset, price: i128);
}

#[contractimpl]
impl OracleTrait for Oracle {
    fn initialize(env: Env, admin: Address, base: Asset, decimals: u32, resolution: u32) {
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
        return env
            .storage()
            .get::<_, Asset>(&DataKey::Base)
            .unwrap()
            .unwrap();
    }

    fn assets(env: Env) -> Vec<Asset> {
        return env
            .storage()
            .get::<_, Vec<Asset>>(&DataKey::Assets)
            .unwrap()
            .unwrap();
    }

    fn decimals(env: Env) -> u32 {
        return env.storage().get_unchecked(&DataKey::Decimals).unwrap();
    }

    fn resolution(env: Env) -> u32 {
        return env
            .storage()
            .get::<_, u32>(&DataKey::Resolution)
            .unwrap()
            .unwrap();
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
                        for price_data_vec_item_result in prices_vec.iter() {
                            let price_data = price_data_vec_item_result.unwrap();
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
                        for (index_usize, price_data_vec_item_result) in
                            prices_vec.iter().enumerate()
                        {
                            let index: u32 = index_usize.try_into().unwrap();
                            if index < starting_index {
                                continue;
                            }
                            let price_data = price_data_vec_item_result.unwrap();
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
        for price_data_result in prices.iter() {
            return Some(price_data_result.unwrap());
        }
        return None;
    }

    fn add_price(env: Env, source: u32, asset: Asset, price: i128) {
        get_admin(&env).require_auth();
        let source_map: Map<u32, Map<Asset, Vec<PriceData>>> =
            env.storage().get_unchecked(&DataKey::Prices).unwrap();
        let asset_map_option = source_map.get(source);
        match asset_map_option {
            Some(asset_map_result) => {
                let asset_map = asset_map_result.unwrap();
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
                price_data_vec.push_back(PriceData::new(price, timestamp))
            }
            None => return,
        }
    }
}
