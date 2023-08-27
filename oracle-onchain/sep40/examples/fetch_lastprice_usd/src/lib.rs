#![no_std]

use soroban_sdk::{contract, contractimpl, Address, Env, Symbol};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

#[contract]
pub struct OracleConsumer;

#[contractimpl]
impl OracleConsumer {
    pub fn add_price_usd(env: Env, contract: Address, price: i128, timestamp: u64) {
        let client = oracle::Client::new(&env, &contract);
        let asset = oracle::Asset::Other(Symbol::new(&env, "USD"));
        return client.add_price(&0, &asset, &price, &timestamp);
    }
    pub fn lastprice_usd(env: Env, contract: Address) -> Option<oracle::PriceData> {
        let client = oracle::Client::new(&env, &contract);
        let asset = oracle::Asset::Other(Symbol::new(&env, "USD"));
        return client.lastprice(&asset);
    }
}

mod test;
