#![cfg(test)]

extern crate std;
use std::println;

use super::{PaymentContract, PaymentContractClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test() {
    let env: Env = Default::default();

    let contract_id = env.register_contract(None, PaymentContract);

    let client = PaymentContractClient::new(&env, &contract_id);

    let from = Address::random(&env);
    let to = Address::random(&env);

    // generate token id
    let token = &env.register_stellar_asset_contract(from.clone());

    println!("token: {:?}", token);

    // get balance
    client.send(&from, &to, &100, &token);

    //println!("balance: {}", balance);
}
