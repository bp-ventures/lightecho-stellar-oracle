#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, Env};

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Payment,
}

#[derive(Clone)]
#[contracttype]
pub struct Payment {
    pub buyer: Address,
    pub seller: Address,
    pub amount: u32,
}

pub struct PaymentContract;

#[contractimpl]
impl PaymentContract {
    // create payment
    pub fn create(e: Env, buyer: Address, seller: Address, amount: u32) {
        if e.storage().has(&DataKey::Payment) {
            panic!("payment is already created");
        }
        let payment = Payment {
            buyer,
            seller,
            amount,
        };
        e.storage().set(&DataKey::Payment, &payment);
    }

    // update payment
    pub fn update(e: Env, buyer: Address, seller: Address, amount: u32) {
        if !e.storage().has(&DataKey::Payment) {
            panic!("payment is not created");
        }
        let payment = Payment {
            buyer,
            seller,
            amount,
        };
        e.storage().set(&DataKey::Payment, &payment);
    }

    // get payment
    pub fn get(e: Env) -> Payment {
        if !e.storage().has(&DataKey::Payment) {
            panic!("payment is not created");
        }
        e.storage().get_unchecked(&DataKey::Payment).unwrap()
    }

    // delete payment
    pub fn delete(e: Env) {
        if !e.storage().has(&DataKey::Payment) {
            panic!("payment is deleted");
        }
        e.storage().delete(&DataKey::Payment);
    }
}

mod test;
