use crate::types::{Asset, PriceDataKey};
use soroban_sdk::Env;

pub fn get_asset_as_u32(env: &Env, asset: Asset) -> Option<u32> {
    let asset_u32: Option<u32>;

    match asset {
        Asset::Stellar(address) => {
            asset_u32 = env.storage().instance().get(&address);
        }
        Asset::Other(symbol) => {
            asset_u32 = env.storage().instance().get(&symbol);
        }
    }
    if asset_u32.is_none() {
        return None;
    }
    return Some(asset_u32.unwrap());
}

/// Returns a 128-bit data key from the given source, asset, and timestamp.
/// The 128-bit data key is then used as a ledger key for storing the price
/// in the blockchain.
pub fn to_price_data_key(source_u32: u32, asset_u32: u32, timestamp_u64: u64) -> PriceDataKey {
    let source_part = (source_u32 as u128) << 96;
    let asset_part = (asset_u32 as u128) << 64;
    let timestamp_part = timestamp_u64 as u128;
    source_part | asset_part | timestamp_part
}
