#![no_std]

use soroban_sdk::{contractimpl, Address, Env, Symbol};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

pub struct OracleConsumer;

#[contractimpl]
impl OracleConsumer {
    pub fn add_price_usd(env: Env, contract: Address, price: i128) {
        let client = oracle::Client::new(&env, &contract);
        let asset = oracle::Asset::Other(Symbol::new(&env, "USD"));
        return client.add_price(&0, &asset, &price);
    }
    pub fn lastprice_usd(env: Env, contract: Address) -> Option<oracle::PriceData> {
        let client = oracle::Client::new(&env, &contract);
        let asset = oracle::Asset::Other(Symbol::new(&env, "USD"));
        return client.lastprice(&asset);
    }
}

mod test;
