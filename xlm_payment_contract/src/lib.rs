#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, BytesN, Env};

mod token {
    soroban_sdk::contractimport!(file = "../utils/token/soroban_token_spec.wasm");
}

#[derive(Clone)]
#[contracttype]

pub enum DataKey {
    Payment,
}

#[derive(Clone)]
#[contracttype]

pub struct Payment {
    pub from: Address,
    pub to: Address,
    pub amount: i128,
    pub token_id: BytesN<32>,
}

pub struct PaymentContract;

#[contractimpl]
impl PaymentContract {
    // send payment
    pub fn send(e: Env, from: Address, to: Address, amount: i128, token_id: BytesN<32>) {
        // define client
        let client = token::Client::new(&e, &token_id);

        from.require_auth();

        client.transfer(&from, &to, &amount);

        //transfer
    }
}

mod test;
