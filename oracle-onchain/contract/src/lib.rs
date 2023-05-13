#![no_std]

use soroban_sdk::{contractimpl, contracttype, Bytes, Env, Map, Symbol};

#[derive(Clone, Copy)]
#[contracttype]
#[repr(u32)]
pub enum DataKey {
    Base = 0,
    Rates = 1,
}

#[derive(Clone, Copy)]
#[contracttype]
pub struct RateEntry {
    pub rate: u128,
    pub decimals: u128,
    pub timestamp: u64,
}

struct Oracle;

impl RateEntry {
    pub fn new(rate: u128, decimals: u128, timestamp: u64) -> Self {
        Self {
            rate,
            decimals,
            timestamp,
        }
    }
}

pub trait OracleTrait {
    fn get_base(env: Env) -> Option<Symbol>;
    fn get_rate(
        env: Env,
        asset_code: Symbol,
        asset_issuer: Option<Bytes>,
        source: u64,
    ) -> Option<RateEntry>;

    fn set_base(env: Env, base: Symbol);
    fn set_rate(
        env: Env,
        asset_code: Symbol,
        asset_issuer: Option<Bytes>,
        source: u64,
        rate: u128,
        decimals: u128,
        timestamp: u64,
    );
    fn remove_rate(env: Env, asset_code: Symbol, asset_issuer: Option<Bytes>, source: u64);
    fn remove_all_rates(env: Env);
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
