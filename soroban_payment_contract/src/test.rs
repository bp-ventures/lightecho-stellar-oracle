#![cfg(test)]
extern crate std;
use std::println;

use super::{PaymentContract, PaymentContractClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]

fn test() {
    // Create a new environment for each test

    let env: Env = Default::default();

    // Register the contract and get the contract id

    let contract_id = env.register_contract(None, PaymentContract);

    // Create a new client for the contract

    let client = PaymentContractClient::new(&env, &contract_id);

    // Create a random address for the buyer

    let buyer = Address::random(&env);

    // Create a random address for the seller

    let seller = Address::random(&env);

    // Create a new payment

    client.create(&buyer, &seller, &100);

    // Get the payment

    let payment = client.get();

    // Check that the payment is correct

    assert_eq!(payment.buyer, buyer);

    assert_eq!(payment.seller, seller);

    assert_eq!(payment.amount, 100);

    // Print the payment

    println!("Getted payment:");

    println!("Buyer: {:?}", payment.buyer);

    println!("Seller: {:?}", payment.seller);

    println!("Amount: {}", payment.amount);
}
