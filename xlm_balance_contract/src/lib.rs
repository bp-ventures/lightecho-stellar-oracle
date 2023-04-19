#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, BytesN, Env};

mod token {
    soroban_sdk::contractimport!(file = "../utils/token/soroban_token_spec.wasm");
}

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Balance,
}

#[derive(Clone)]
#[contracttype]
pub struct Balance {
    pub address: Address,
    pub balance: i128,
}

pub struct BalanceContract;

#[contractimpl]
impl BalanceContract {
    // get balance
    pub fn balance(e: Env, address: Address, token_id: BytesN<32>) -> i128 {
        // define client
        let client = token::Client::new(&e, &token_id);

        let balance = client.balance(&address);

        // return balance
        // The horizon endpoint automatically adds a decimal such that Assets are denoted with 7 decimal places.
        // Numbers are not stored on chain with decimals, so the number you are receiving via CLI is the same as the one being returned by your Horizon query.
        balance
    }
}

mod test;
