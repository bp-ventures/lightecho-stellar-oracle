#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, BytesN, Env};

mod token {
    soroban_sdk::contractimport!(file = "../utils/token/soroban_token_spec.wasm");
}

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Balance(Address),
}

pub struct SAContract;

#[contractimpl]
impl SAContract {
    // get balance
    fn get_balance(e: Env, address: Address, token_id: BytesN<32>) -> i128 {
        let client = token::Client::new(&e, &token_id);

        // client.xfer(e, &to, &amount);
        let balance = client.balance(&address);

        e.storage().set(&DataKey::Balance(address), &balance);

        balance
    }
}

mod test;
