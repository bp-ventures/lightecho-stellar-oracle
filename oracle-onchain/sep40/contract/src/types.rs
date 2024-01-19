use soroban_sdk::{contracttype, Address, Symbol};

pub type PriceDataKey = u128;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
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

/// Internal Price struct.
/// Used to facilitate adding prices to the contract from the SDK.
#[derive(Clone, Debug)]
#[contracttype]
pub struct InternalPrice {
    pub source: u32,
    pub asset: Asset,
    pub asset_u32: u32,
    pub price: i128,
    pub timestamp: u64,
}

/// Internal Asset struct.
/// Used to facilitate adding assets to the contract from the SDK.
#[derive(Clone, Debug)]
#[contracttype]
pub struct InternalAsset {
    pub asset: Asset,
    pub asset_u32: u32,
}
