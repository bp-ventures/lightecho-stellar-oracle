#![cfg(test)]

use crate::contract::{PriceUpDown, PriceUpDownClient};
use crate::oracle;
use soroban_sdk::{testutils::Address as _, Address, Env};
extern crate std;

#[test]
fn test_price_up() {
    let env = Env::default();
    env.budget().reset_unlimited();
    let oracle_id = env.register_contract_wasm(None, oracle::WASM);
    let oracle_client = oracle::Client::new(&env, &oracle_id);
    oracle_client.initialize(
        &Address::random(&env),
        &oracle::Asset::Stellar(Address::random(&env)),
        &18,
        &60,
    );
    env.mock_all_auths();
    let consumer_contract_id = env.register_contract(None, PriceUpDown);
    let price_up_down_client = PriceUpDownClient::new(&env, &consumer_contract_id);
    price_up_down_client.initialize(&oracle_id);
    let source = 0;
    let asset = oracle::Asset::Stellar(Address::random(&env));
    let mut timestamp = env.ledger().timestamp();
    oracle_client.add_price(&source, &asset, &1, &timestamp);
    let up_down = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(up_down.up, false);
    assert_eq!(up_down.down, false);
    assert_eq!(up_down.equal, true);
    timestamp = timestamp + 1;
    oracle_client.add_price(&source, &asset, &2, &timestamp);
    let up_down = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(up_down.up, true);
    assert_eq!(up_down.down, false);
    assert_eq!(up_down.equal, false);
}

#[test]
fn test_price_down() {
    let env = Env::default();
    env.budget().reset_unlimited();
    let oracle_id = env.register_contract_wasm(None, oracle::WASM);
    let oracle_client = oracle::Client::new(&env, &oracle_id);
    oracle_client.initialize(
        &Address::random(&env),
        &oracle::Asset::Stellar(Address::random(&env)),
        &18,
        &60,
    );
    env.mock_all_auths();
    let consumer_contract_id = env.register_contract(None, PriceUpDown);
    let price_up_down_client = PriceUpDownClient::new(&env, &consumer_contract_id);
    price_up_down_client.initialize(&oracle_id);
    let source = 0;
    let asset = oracle::Asset::Stellar(Address::random(&env));
    let mut timestamp = env.ledger().timestamp();
    oracle_client.add_price(&source, &asset, &2, &timestamp);
    let lastprice = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(lastprice.up, false);
    assert_eq!(lastprice.down, false);
    assert_eq!(lastprice.equal, true);
    timestamp = timestamp + 1;
    oracle_client.add_price(&source, &asset, &1, &timestamp);
    let lastprice = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(lastprice.up, false);
    assert_eq!(lastprice.down, true);
    assert_eq!(lastprice.equal, false);
}

#[test]
fn test_price_equal() {
    let env = Env::default();
    env.budget().reset_unlimited();
    let oracle_id = env.register_contract_wasm(None, oracle::WASM);
    let oracle_client = oracle::Client::new(&env, &oracle_id);
    oracle_client.initialize(
        &Address::random(&env),
        &oracle::Asset::Stellar(Address::random(&env)),
        &18,
        &60,
    );
    env.mock_all_auths();
    let consumer_contract_id = env.register_contract(None, PriceUpDown);
    let price_up_down_client = PriceUpDownClient::new(&env, &consumer_contract_id);
    price_up_down_client.initialize(&oracle_id);
    let source = 0;
    let asset = oracle::Asset::Stellar(Address::random(&env));
    let mut timestamp = env.ledger().timestamp();
    oracle_client.add_price(&source, &asset, &1, &timestamp);
    let lastprice = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(lastprice.up, false);
    assert_eq!(lastprice.down, false);
    assert_eq!(lastprice.equal, true);
    timestamp = timestamp + 1;
    oracle_client.add_price(&source, &asset, &1, &timestamp);
    let lastprice = price_up_down_client.get_price_up_down(&asset);
    assert_eq!(lastprice.up, false);
    assert_eq!(lastprice.down, false);
    assert_eq!(lastprice.equal, true);
}
