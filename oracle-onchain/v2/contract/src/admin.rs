use crate::metadata;
use crate::storage_types::{Asset, DataKey, PriceData, BALANCE_BUMP_AMOUNT};
use soroban_sdk::{Address, Env, Map, Vec};

pub fn has_admin(env: &Env) -> bool {
    return env.storage().instance().has(&DataKey::Admin);
}

pub fn read_admin(env: &Env) -> Address {
    return env.storage().instance().get(&DataKey::Admin).unwrap();
}

pub fn write_admin(env: &Env, id: &Address) {
    return env.storage().instance().set(&DataKey::Admin, id);
}

fn is_u32_in_vec(n: u32, vec: &Vec<u32>) -> bool {
    for item in vec.iter() {
        if item == n {
            return true;
        }
    }
    return false;
}

fn is_asset_in_vec(asset: Asset, vec: &Vec<Asset>) -> bool {
    for item in vec.iter() {
        if item == asset {
            return true;
        }
    }
    return false;
}

pub fn add_price(env: &Env, source: &u32, asset: &Asset, price: &i128) {
    read_admin(&env).require_auth();
    let mut prices = metadata::read_prices(&env);
    let asset_map_option = prices.get(*source);
    let mut asset_map;
    match asset_map_option {
        Some(asset_map_result) => asset_map = asset_map_result,
        None => {
            asset_map = Map::<Asset, Vec<PriceData>>::new(&env);
        }
    }
    let price_data_vec_option = asset_map.get(asset.clone());
    let mut price_data_vec;
    match price_data_vec_option {
        Some(price_data_vec_result) => {
            price_data_vec = price_data_vec_result;
        }
        None => {
            price_data_vec = Vec::<PriceData>::new(&env);
        }
    }
    let timestamp = env.ledger().timestamp();
    if price_data_vec.len() >= 10 {
        price_data_vec.pop_front();
    }
    price_data_vec.push_back(PriceData::new(*price, timestamp));
    asset_map.set(asset.clone(), price_data_vec);
    prices.set(*source, asset_map);
    metadata::write_prices(env, &prices);
}

pub fn remove_prices(
    env: &Env,
    sources: &Vec<u32>,
    assets: &Vec<Asset>,
    start_timestamp: &Option<u64>,
    end_timestamp: &Option<u64>,
) {
    read_admin(&env).require_auth();
    let prices = metadata::read_prices(env);
    let mut new_prices = Map::<u32, Map<Asset, Vec<PriceData>>>::new(&env);
    let sources_len = sources.len();
    let assets_len = assets.len();
    for (source, asset_map) in prices.iter() {
        if sources_len > 0 && !is_u32_in_vec(source, &sources) {
            new_prices.set(source, asset_map);
            continue;
        }
        let mut new_asset_map = Map::<Asset, Vec<PriceData>>::new(&env);
        for (asset, price_data_vec) in asset_map.iter() {
            if assets_len > 0 && !is_asset_in_vec(asset.clone(), &assets) {
                new_asset_map.set(asset.clone(), price_data_vec);
                continue;
            }
            let mut new_price_data_vec = Vec::<PriceData>::new(&env);
            for price_data in price_data_vec.iter() {
                match start_timestamp {
                    Some(t) => {
                        if *t < price_data.timestamp {
                            new_price_data_vec.push_back(price_data);
                            continue;
                        }
                    }
                    None => {}
                }
                match end_timestamp {
                    Some(t) => {
                        if *t > price_data.timestamp {
                            new_price_data_vec.push_back(price_data);
                            continue;
                        }
                    }
                    None => {}
                }
            }
            if new_price_data_vec.len() > 0 {
                new_asset_map.set(asset.clone(), new_price_data_vec)
            }
        }
        if new_asset_map.keys().len() > 0 {
            new_prices.set(source, new_asset_map);
        }
    }
    metadata::write_prices(env, &new_prices);
}
