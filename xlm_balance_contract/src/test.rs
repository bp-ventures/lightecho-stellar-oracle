#![cfg(test)]

extern crate std;
use std::println;

use super::{BalanceContract, BalanceContractClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test() {
    let env: Env = Default::default();

    let contract_id = env.register_contract(None, BalanceContract);

    let client = BalanceContractClient::new(&env, &contract_id);

    //let address = "GALGFV6YVKMVAWHK6QA7GCC67VKBW73A3PB5IKZGKT5ID5AGK4S3Y7GX";
    let address = Address::random(&env);

    // generate token id
    let token = &env.register_stellar_asset_contract(address.clone());

    println!("token: {:?}", token);

    // get balance
    let balance = client.get_balance(&address, token);

    println!("balance: {}", balance);
}
