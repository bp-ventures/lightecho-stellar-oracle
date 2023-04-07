#![cfg(test)]

use super::{PriceUpdate, PriceUpdateClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test() {
    // Create a new environment for each test
    let env: Env = Default::default();

    // Register the contract and get the contract id
    let contract_id = env.register_contract(None, PriceUpdate);

    // Create a new client for the contract
    let client = PriceUpdateClient::new(&env, &contract_id);

    // Create a random address for the seller
    let seller = Address::random(&env);
    let sell_price = 100;
    let buy_price = 200;

    // Create a new price update
    client.create(&seller, &sell_price, &buy_price);

    // Get the price update
    let price = client.get();

    // Check that the price update is correct
    assert_eq!(price.seller, seller);
    assert_eq!(price.sell_price, sell_price);
    assert_eq!(price.buy_price, buy_price);
}
