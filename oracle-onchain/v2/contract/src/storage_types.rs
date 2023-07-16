use soroban_sdk::{contracttype, Address, Symbol};

pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 34560; // 2 days
pub(crate) const PERSISTENT_BUMP_AMOUNT: u32 = 518400; // 30 days

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
