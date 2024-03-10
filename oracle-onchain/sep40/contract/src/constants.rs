use soroban_sdk::{Symbol, symbol_short};

pub const ADMIN: &str = "admin";
pub const LAST_TIMESTAMP: &str = "last_timestamp";
pub const SOURCES: &str = "sources";
pub const ASSETS: &str = "assets";
pub const BASE_ASSET: &str = "base_asset";
pub const DECIMALS: &str = "decimals";
pub const RESOLUTION: &str = "resolution";
pub const TEMPORARY_KEY_TTL: u32 = 151200; // approx. 7 days in ledgers

pub const TOPIC_NEW_PRICES: Symbol = symbol_short!("newprices");
pub const TOPIC_LIGHTECHO: Symbol = symbol_short!("lightecho");
