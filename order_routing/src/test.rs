#![cfg(test)]
extern crate alloc;
extern crate std;

use std::println;

use crate::{token, SingleOrderClient};
use alloc::string::String;
use soroban_sdk::{symbol, testutils::Address as _, Address, BytesN, Env, IntoVal};

fn create_token_contract(e: &Env, admin: &Address) -> token::Client {
    token::Client::new(&e, &e.register_stellar_asset_contract(admin.clone()))
}

fn create_single_offer_contract(
    e: &Env,
    seller: &Address,
    sell_token: &BytesN<32>,
    buy_token: &BytesN<32>,
    sell_price: u32,
    buy_price: u32,
) -> SingleOrderClient {
    let offer = SingleOrderClient::new(e, &e.register_contract(None, crate::SingleOrder {}));
    offer.create(seller, sell_token, buy_token, &sell_price, &buy_price);

    // Verify that authorization is required for the seller.
    assert_eq!(
        e.recorded_top_authorizations(),
        std::vec![(
            seller.clone(),
            offer.contract_id.clone(),
            symbol!("create"),
            (
                seller,
                sell_token.clone(),
                buy_token.clone(),
                sell_price,
                buy_price
            )
                .into_val(e)
        )]
    );

    offer
}

fn create_new_order() {
    let e: Env = Default::default();
    let token_admin = Address::random(&e);
    let seller = Address::random(&e);
    let buyer = Address::random(&e);
    let sell_token = create_token_contract(&e, &token_admin);
    let buy_token = create_token_contract(&e, &token_admin);

    // The price here is 1 sell_token for 2 buy_token.
    let offer = create_single_offer_contract(
        &e,
        &seller,
        &sell_token.contract_id,
        &buy_token.contract_id,
        1,
        2,
    );
    let offer_address = Address::from_contract_id(&e, &offer.contract_id);

    // Give some sell_token to seller and buy_token to buyer.
    sell_token.mint(&token_admin, &seller, &1000);
    buy_token.mint(&token_admin, &buyer, &1000);

    // Deposit 100 sell_token from seller into offer.
    sell_token.xfer(&seller, &offer_address, &100);

    // Try trading 20 buy_token for at least 11 sell_token - that wouldn't
    // succeed because the offer price would result in 10 sell_token.
    assert!(offer.try_trade(&buyer, &20_i128, &11_i128).is_err());

    // Buyer trades 20 buy_token for 10 sell_token.
    offer.trade(&buyer, &20_i128, &10_i128);

    // Verify that authorization is required for the buyer.
    assert_eq!(
        e.recorded_top_authorizations(),
        std::vec![(
            buyer.clone(),
            offer.contract_id.clone(),
            symbol!("trade"),
            (&buyer, 20_i128, 10_i128).into_val(&e)
        )]
    );

    assert_eq!(sell_token.balance(&seller), 900);
    assert_eq!(sell_token.balance(&buyer), 10);
    assert_eq!(sell_token.balance(&offer_address), 90);
    assert_eq!(buy_token.balance(&seller), 20);
    assert_eq!(buy_token.balance(&buyer), 980);
    assert_eq!(buy_token.balance(&offer_address), 0);

    // Withdraw 70 sell_token from offer.
    offer.withdraw(&sell_token.contract_id, &70);
    // Verify that the seller has to authorize this.
    assert_eq!(
        e.recorded_top_authorizations(),
        std::vec![(
            seller.clone(),
            offer.contract_id.clone(),
            symbol!("withdraw"),
            (sell_token.contract_id.clone(), 70_i128).into_val(&e)
        )]
    );

    assert_eq!(sell_token.balance(&seller), 970);
    assert_eq!(sell_token.balance(&offer_address), 20);

    // The price here is 1 sell_token = 1 buy_token.
    offer.updt_price(&1, &1);
    // Verify that the seller has to authorize this.
    assert_eq!(
        e.recorded_top_authorizations(),
        std::vec![(
            seller.clone(),
            offer.contract_id.clone(),
            symbol!("updt_price"),
            (1_u32, 1_u32).into_val(&e)
        )]
    );

    // Buyer trades 10 buy_token for 10 sell_token.
    offer.trade(&buyer, &10_i128, &9_i128);
    assert_eq!(sell_token.balance(&seller), 970);
    assert_eq!(sell_token.balance(&buyer), 20);
    assert_eq!(sell_token.balance(&offer_address), 10);
    assert_eq!(buy_token.balance(&seller), 30);
    assert_eq!(buy_token.balance(&buyer), 970);
    assert_eq!(buy_token.balance(&offer_address), 0);
}

// get price of asset from the liquidity pool
// fn get_lp_asset_price(e: &Env, asset: &BytesN<32>) -> u32 {
//     let lp = e
//         .storage()
//         .get_unchecked(&DataKey::LiquidityPool(asset.clone()))
//         .unwrap();
//     let lp_client = token::Client::new(&e, &lp);
//     let lp_supply = lp_client.total_supply();
//     let asset_supply = token::Client::new(&e, &asset).total_supply();
//     (asset_supply / lp_supply) as u32
// }
// get price of asset from the oracle
// fn get_oracle_price(e: &Env, asset: &BytesN<32>) -> u32 {
//     let oracle = e
//         .storage()
//         .get_unchecked(&DataKey::Oracle(asset.clone()))
//         .unwrap();
//     let oracle_client = oracle::Client::new(&e, &oracle);
//     oracle_client.get_price()
// }

// get best price of sell in DEX
// fn get_best_sell_price(e: &Env, sell_asset: &BytesN<32>, buy_asset: &BytesN<32>) -> u32 {
//     let lp_price = get_lp_asset_price(&e, &sell_asset);
//     let oracle_price = get_oracle_price(&e, &sell_asset);
//     if lp_price > oracle_price {
//         lp_price
//     } else {
//         oracle_price
//     }
// }

#[test]
fn test() {
    println!("---------------------------------------------------------------------------");
    println!("--------------- Welcome to Soroban Order Routing App ----------------------");
    println!("---------------------------------------------------------------------------");

    println!("Press 1 to create a new order");
    // println!("Press 2 to get the price of Liquidity Pool associated with the asset");
    // println!("Press 3 to get the best price of sell in DEX");
    println!("Press q to quit");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();

    match input.trim() {
        "1" => create_new_order(),
        //"2" => println!("Get LP asset price"),
        //"3" => println!("Get best price of sell in DEX"),
        "q" => std::process::exit(0),
        _ => println!("Invalid input"),
    }

    // ToDO:
    // connect to futurenet
    // if the a is greater than 1% of the asset pool ignore the liquidity pool info (> 0.01 * lp_a_0)
    // console data input and output
    // add more tests
    // use stellar sdk to get the price of the asset
    // UI interface or endpoints
}
