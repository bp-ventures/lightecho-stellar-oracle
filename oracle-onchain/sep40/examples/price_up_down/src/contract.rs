use crate::metadata;
use crate::oracle;
use crate::storage_types::{DataKey, UpDown, TEMPORARY_BUMP_AMOUNT, TEMPORARY_LIFETIME_THRESHOLD};
use soroban_sdk::{contract, contractimpl, Address, Env, Map};

pub trait PriceUpDownTrait {
    fn initialize(env: Env, oracle_contract_id: Address);
    fn lastprice(env: Env, asset: oracle::Asset) -> Option<oracle::PriceData>;
    fn get_price_up_down(env: Env, asset: oracle::Asset) -> UpDown;
}

#[contract]
pub struct PriceUpDown;

#[contractimpl]
impl PriceUpDownTrait for PriceUpDown {
    fn initialize(env: Env, oracle_contract_id: Address) {
        if metadata::has_oracle_contract_id(&env) {
            panic!("already initialized")
        }

        metadata::write_metadata(&env, &oracle_contract_id);
        write_prices(&env, &Map::<oracle::Asset, oracle::PriceData>::new(&env));
    }

    fn lastprice(env: Env, asset: oracle::Asset) -> Option<oracle::PriceData> {
        let oracle_contract_id = metadata::read_oracle_contract_id(&env);
        let client = oracle::Client::new(&env, &oracle_contract_id);
        let lastprice = client.lastprice(&asset);
        return lastprice;
    }

    fn get_price_up_down(env: Env, asset: oracle::Asset) -> UpDown {
        let oracle_contract_id = metadata::read_oracle_contract_id(&env);
        let client = oracle::Client::new(&env, &oracle_contract_id);
        let lastprice = client.lastprice(&asset);
        if lastprice.is_none() {
            return UpDown {
                up: false,
                down: false,
                equal: false,
            };
        }
        let lastprice = lastprice.unwrap();
        let mut prices = read_prices(&env);
        let stored_price_option = prices.get(asset.clone());
        prices.set(asset.clone(), lastprice.clone());
        write_prices(&env, &prices);
        match stored_price_option {
            Some(stored_price) => {
                return UpDown {
                    up: lastprice.price > stored_price.price,
                    down: lastprice.price < stored_price.price,
                    equal: lastprice.price == stored_price.price,
                };
            }
            None => {
                return UpDown {
                    up: false,
                    down: false,
                    equal: true,
                };
            }
        }
    }
}

pub fn read_prices(env: &Env) -> Map<oracle::Asset, oracle::PriceData> {
    let key = DataKey::Prices;
    env.storage()
        .temporary()
        .bump(&key, TEMPORARY_LIFETIME_THRESHOLD, TEMPORARY_BUMP_AMOUNT);
    return env.storage().temporary().get(&key).unwrap();
}

pub fn write_prices(env: &Env, prices: &Map<oracle::Asset, oracle::PriceData>) {
    let key = DataKey::Prices;
    env.storage()
        .temporary()
        .bump(&key, TEMPORARY_LIFETIME_THRESHOLD, TEMPORARY_BUMP_AMOUNT);
    return env.storage().temporary().set(&key, prices);
}
