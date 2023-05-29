#![no_std]

use soroban_sdk::{contractimpl, contracttype, Bytes, Env, Map, Address, Symbol};

#[derive(Clone, Copy)]
#[contracttype]
#[repr(u32)]
pub enum DataKey {
    Base = 0,
    Rates = 1,
}

#[derive(Clone, Copy)]
#[contracttype]
pub struct PriceData {
    price: u128,
    timestamp: u64,
}

struct Oracle;

impl PriceData {
    pub fn new(price: u128, timestamp: u64) -> Self {
        Self { price, timestamp }
    }
}

pub trait OracleTrait {
    /// Return the base asset the price is reported in
    fn base(env: Env) -> Symbol;
    /// Return all assets quoted by the price feed
    fn assets(env: Env) -> Vec<Symbol>;
    /// Return the number of decimals for all assets quoted by the oracle
    fn decimals(env: Env) -> u32;
    /// Return default tick period timeframe (in seconds)
    fn resolution(env: Env) -> u32;
    /// Get price from source=0 in base asset at specific timestamp
    fn price(env: Env, asset: Symbol, timestamp: u64) -> Option<PriceData>;
    /// Get price from source=<source> in base asset at specific timestamp
    fn price(env: Env, source: u32, asset: Symbol, timestamp: u64) -> Option<PriceData>;
    /// Get last N price records
    fn prices(env: Env, asset: Symbol, records: u32) -> Option<Vec<PriceData>>;
    /// Get the most recent price for an asset
    fn lastprice(env: Env, asset: Symbol) -> Option<PriceData>;

    /// Set price of source in base asset at specific timestamp
    fn set_price(env: Env, source: u32, asset: Symbol, timestamp: u64, price: u128);
    /// Remove 
    fn remove_prices(env: Env, source: u32);
    /// Remove all prices of source
    fn remove_prices(env: Env, source: u32);
    //TODO remove price
    //TODO remove all prices
}

fn all_rates(env: &Env) -> Map<(Symbol, Option<Bytes>, u64), RateEntry> {
    if let Some(rates) = env.storage().get(&DataKey::Rates) {
        return rates.unwrap();
    }

    return Map::<(Symbol, Option<Bytes>, u64), RateEntry>::new(&env);
}

#[contractimpl]
impl OracleTrait for Oracle {
    // Getters
    fn get_base(env: Env) -> Option<Symbol> {
        let base = match env.storage().get(&DataKey::Base) {
            Some(_base) => _base.unwrap(),
            None => return None,
        };
        return Some(base);
    }

    fn get_rate(
        env: Env,
        asset_code: Symbol,
        asset_issuer: Option<Bytes>,
        source: u64,
    ) -> Option<RateEntry> {
        let rates = all_rates(&env);
        let rate = match rates.get((asset_code, asset_issuer, source)) {
            Some(_rate) => _rate.unwrap(),
            None => return None,
        };
        Some(rate)
    }

    // Setters
    fn set_base(env: Env, base: Symbol) {
        env.storage().set(&DataKey::Base, &base);
    }

    fn set_rate(
        env: Env,
        asset_code: Symbol,
        asset_issuer: Option<Bytes>,
        source: u64,
        rate: u128,
        decimals: u128,
        timestamp: u64,
    ) {
        let mut rates = all_rates(&env);
        rates.set(
            (asset_code, asset_issuer, source),
            RateEntry {
                rate,
                decimals,
                timestamp,
            },
        );
        env.storage().set(&DataKey::Rates, &rates);
    }

    fn remove_rate(env: Env, asset_code: Symbol, asset_issuer: Option<Bytes>, source: u64) {
        let mut rates = all_rates(&env);
        rates.remove((asset_code, asset_issuer, source));
        env.storage().set(&DataKey::Rates, &rates);
    }

    fn remove_all_rates(env: Env) {
        env.storage().remove(&DataKey::Rates)
    }
}
