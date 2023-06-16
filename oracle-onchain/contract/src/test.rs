#![cfg(test)]

use crate::{v2::Asset, v2::Oracle, v2::OracleClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test_base() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.base(), base);
}

#[test]
fn test_decimals() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.decimals(), decimals);
}
