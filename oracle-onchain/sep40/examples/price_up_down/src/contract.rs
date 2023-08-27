use crate::metadata;
use crate::storage_types::{DataKey, UpDown, TEMPORARY_BUMP_AMOUNT};
use soroban_sdk::{contract, contractimpl, Address, Env, Map};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

pub trait PriceUpDownTrait {
    fn initialize(env: Env, oracle_contract_id: Address);
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
        prices.set(asset.clone(), lastprice.clone());
        write_prices(&env, &prices);
        let stored_price_option = prices.get(asset.clone());
        match stored_price_option {
            Some(stored_price) => {
                return UpDown {
                    up: stored_price.price > lastprice.price,
                    down: stored_price.price < lastprice.price,
                    equal: stored_price.price == lastprice.price,
                };
            }
            None => {
                return UpDown {
                    up: false,
                    down: false,
                    equal: false,
                };
            }
        }
    }
}

pub fn read_prices(env: &Env) -> Map<oracle::Asset, oracle::PriceData> {
    let key = DataKey::Prices;
    env.storage().temporary().bump(&key, TEMPORARY_BUMP_AMOUNT);
    return env.storage().temporary().get(&key).unwrap();
}

pub fn write_prices(env: &Env, prices: &Map<oracle::Asset, oracle::PriceData>) {
    let key = DataKey::Prices;
    env.storage().temporary().bump(&key, TEMPORARY_BUMP_AMOUNT);
    return env.storage().temporary().set(&key, prices);
}
