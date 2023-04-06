#![cfg(test)]

use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test() {
    let env: Env = Default::default();

    let seller = Address::random(&env);
    let sell_price = 100;
    let buy_price = 200;

    super::PriceUpdate::create(env, seller, sell_price, buy_price);

    super::PriceUpdate::get(env);

    // let price = super::get_price(&env);
    // assert_eq!(price.seller, seller);
    // assert_eq!(price.sell_price, sell_price);
    // assert_eq!(price.buy_price, buy_price);
}
