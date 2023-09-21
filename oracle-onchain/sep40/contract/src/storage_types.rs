use soroban_sdk::{contracttype, Address, Env, Symbol};

pub(crate) const ONE_MINUTE_IN_LEDGERS: u32 = 12;
pub(crate) const DAY_IN_LEDGERS: u32 = 17280;

pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 7 * DAY_IN_LEDGERS;
pub(crate) const INSTANCE_LIFETIME_THRESHOLD: u32 = INSTANCE_BUMP_AMOUNT - DAY_IN_LEDGERS;

pub(crate) const TEMPORARY_BUMP_AMOUNT: u32 = 10 * ONE_MINUTE_IN_LEDGERS;
pub(crate) const TEMPORARY_LIFETIME_THRESHOLD: u32 = TEMPORARY_BUMP_AMOUNT - ONE_MINUTE_IN_LEDGERS;

//pub(crate) const PERSISTENT_BUMP_AMOUNT: u32 = 30 * DAY_IN_LEDGERS;
//pub(crate) const PERSISTENT_LIFETIME_THRESHOLD: u32 = PERSISTENT_BUMP_AMOUNT - DAY_IN_LEDGERS;

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

pub fn bump_temporary(env: &Env, key: &DataKey) {
    env.storage()
        .temporary()
        .bump(key, TEMPORARY_LIFETIME_THRESHOLD, TEMPORARY_BUMP_AMOUNT);
}

pub fn bump_instance(env: &Env) {
    env.storage()
        .instance()
        .bump(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}

//pub fn bump_persistent(env: &Env, key: &DataKey) {
//    env.storage()
//        .persistent()
//        .bump(key, PERSISTENT_LIFETIME_THRESHOLD, PERSISTENT_BUMP_AMOUNT);
//}
