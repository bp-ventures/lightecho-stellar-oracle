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
    pub fn get_balance(e: Env, address: Address, token_id: BytesN<32>) -> i128 {
        // define client
        let client = token::Client::new(&e, &token_id);

        // client.xfer(e, &to, &amount);
        let balance = client.balance(&address);

        // return balance
        balance

        //e.storage().set(&DataKey::Balance(address), &balance);
    }
}

mod test;
