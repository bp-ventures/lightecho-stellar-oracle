use soroban_sdk::{contracttype, Address, Env, Symbol};

pub(crate) const DAY_IN_LEDGERS: u32 = 17280;

pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 7 * DAY_IN_LEDGERS;
pub(crate) const INSTANCE_LIFETIME_THRESHOLD: u32 = INSTANCE_BUMP_AMOUNT - DAY_IN_LEDGERS;

#[derive(Clone, Copy)]
#[contracttype]
pub enum DataKey {
    Admin = 0,
    Base = 1,
    Decimals = 2,
    Resolution = 3,
    Prices = 4,
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

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub enum Asset {
    Stellar(Address),
    Other(Symbol),
}

#[derive(Clone, Debug)]
#[contracttype]
pub struct Price {
    pub source: u32,
    pub asset: Asset,
    pub price: i128,
    pub timestamp: u64,
}

pub fn bump_instance(env: &Env) {
    env.storage()
        .instance()
        .extend_ttl(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}
