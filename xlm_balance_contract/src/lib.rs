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
    fn token(e: Env, token_id: BytesN<32>) {
        let client = token::Client::new(&e, &token_id);

        // client.xfer(e, &to, &amount);
        
    }
}

mod test;
