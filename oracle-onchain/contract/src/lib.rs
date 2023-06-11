#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, Env, Map, String, Symbol, Vec};

#[derive(Clone, Copy)]
#[contracttype]
#[repr(u32)]
pub enum DataKey {
    Resolution = 0,
    Assets = 1,
    Sources = 2,
}

#[derive(Clone)]
#[contracttype]
enum Asset {
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

struct Oracle;

pub trait OracleTrait {
    /// Return the base asset the price is reported in.
    fn base(env: Env) -> Asset;

    /// Return all assets quoted by the price feed.
    fn assets(env: Env) -> Vec<Asset>;

    /// Return all sources
    fn sources(env: Env) -> Vec<u8>;

    /// Return the number of decimals for all assets quoted by the oracle.
    fn decimals(env: Env) -> u32;

    /// Return default tick period timeframe (in seconds).
    fn resolution(env: Env) -> u32;

    /// Get prices (in base asset) contained in the provided timestamp range,
    /// ordered by oldest to newest.
    /// Both timestamps are inclusive, meaning if there's a price exactly at
    /// `start_timestamp`, it will be included. Same for `end_timestamp`.
    /// Since there are different price sources, this function calculates and
    /// returns the average price from all sources:
    ///   price = average(price_from_source0, price_from_source1, ..., price_from_sourceN)
    fn prices(env: Env, asset: Asset, start_timestamp: u64, end_timestamp: u64) -> Vec<PriceData>;

    fn prices_by_source(
        env: Env,
        source: u8,
        asset: Asset,
        start_timestamp: u64,
        end_timestamp: u64,
    ) -> Vec<PriceData>;

    /// Get last N price records
    fn lastprices(env: Env, asset: Asset, records: u32) -> Vec<PriceData>;

    fn lastprices_by_source(env: Env, source: u8, asset: Asset, records: u32) -> Vec<PriceData>;

    /// Get latest price in base asset at specific timestamp.
    /// The price is the result of this calculation:
    ///   price = average(lastprice_from_source0, lastprice_from_source1, ..., lastprice_from_sourceN)
    /// Which is an average of all the latest prices provided by different sources.
    fn lastprice(env: Env, asset: Asset) -> Option<PriceData>;

    fn lastprice_by_source(env: Env, source: u8, asset: Asset) -> Option<PriceData>;

    fn add_prices(env: Env, source: u8, asset: Asset, price: i128);

    fn remove_prices(
        env: Env,
        sources: Vec<u8>,
        assets: Vec<Asset>,
        start_timestamp: Option<u64>,
        end_timestamp: Option<u64>,
    );
}

#[contractimpl]
impl OracleTrait for Oracle {
    fn base(env: Env) -> Asset {
        return Asset::Other(Symbol::new(&env, "USD"));
    }

    fn assets(env: Env) -> Vec<Asset> {
        return env.storage().get(&DataKey::Assets).unwrap().unwrap();
    }

    fn sources(env: Env) -> Vec<u8> {
        return env.storage().get(&DataKey::Sources).unwrap().unwrap();
    }

    fn decimals(env: Env) -> u32 {
        return 18;
    }

    fn resolution(env: Env) -> u32 {
        return env.storage().get(&DataKey::Resolution).unwrap().unwrap();
    }

    fn prices(env: Env, asset: Asset, start_timestamp: u64, end_timestamp: u64) -> Vec<PriceData> {
        let asset_map_option = env.storage().get(&asset);
        match asset_map_option {
            Some(option) => {
                let asset_map_result = option.unwrap();
                match asset_map_result {
                    Ok(asset_map) => {
                        let price_data = Vec::<PriceData>::new();
                        for (source, price_data_map) in asset_map.iter() {
                            let timestamps: Vec<u64> = price_data_map.keys();
                            timestamps.sort();
                            let start_ts_index = timestamps.len();
                            for (index, timestamp_result) in timestamps.iter().enumerate() {
                                match timestamp_result {
                                    Ok(timestamp) => {
                                        if timestamp >= start_timestamp {
                                            start_ts_index = index;
                                        }
                                    }
                                    Err(error) => break,
                                }
                            }
                            // Remove all elements before start index
                            timestamps = &mut timestamps[start_ts_index..];
                            let end_ts_index = timestamps.len();
                            for (index, timestamp_result) in timestamps.iter().enumerate() {
                                match timestamp_result {
                                    Ok(timestamp) => {
                                        if timestamp > end_timestamp {
                                            end_ts_index = index;
                                        }
                                    }
                                    Err(error) => break,
                                }
                            }
                            // Remove all elements after end index
                            timestamps = &mut timestamps[..end_ts_index];
                            WIP
                        }
                    }
                    Err(error) => return Vec::<PriceData>::new(),
                }
            }
            None => return Vec::<PriceData>::new(),
        }
    }
}
