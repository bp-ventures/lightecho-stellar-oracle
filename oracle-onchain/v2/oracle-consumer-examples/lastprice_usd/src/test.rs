#![cfg(test)]

use crate::{oracle, OracleConsumer, OracleConsumerClient};
use soroban_sdk::{testutils::Address as _, Address, Env};
extern crate std;

#[test]
fn test_lastprice_usd() {
    let env = Env::default();
    let oracle_id = env.register_contract_wasm(None, oracle::WASM);
    let client = oracle::Client::new(&env, &oracle_id);
    client.initialize(
        &Address::random(&env),
        &oracle::Asset::Stellar(Address::random(&env)),
        &18,
        &60,
    );
    let consumer_contract_id = env.register_contract(None, OracleConsumer);
    let client = OracleConsumerClient::new(&env, &consumer_contract_id);
    let lastprice = client.lastprice_usd(&oracle_id);
    assert_eq!(lastprice, None);
    let price: i128 = 1234;
    env.mock_all_auths();
    client.add_price_usd(&oracle_id, &price);
    let lastprice_data = client.lastprice_usd(&oracle_id).unwrap();
    assert_eq!(lastprice_data.price, price);
}
