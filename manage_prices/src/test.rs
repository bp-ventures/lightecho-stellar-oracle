#![cfg(test)]

use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test() {
    // Create a new environment for each test
    let env: Env = Default::default();

    // Create a random address for the seller
    let seller = Address::random(&env);
    let sell_price = 100;
    let buy_price = 200;

    // Create a new price update
    super::PriceUpdate::create(env.clone(), seller.clone(), sell_price, buy_price);

    // Get the price update
    let price = super::PriceUpdate::get(env);

    // Check that the price update is correct
    assert_eq!(price.seller, seller);
    assert_eq!(price.sell_price, sell_price);
    assert_eq!(price.buy_price, buy_price);
}
