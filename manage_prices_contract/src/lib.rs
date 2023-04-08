#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, Env};

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Price,
}

#[derive(Clone)]
#[contracttype]
pub struct Price {
    pub seller: Address,
    pub sell_price: u32,
    pub buy_price: u32,
}

pub struct PriceUpdate;

#[contractimpl]
impl PriceUpdate {
    // create price
    pub fn create(e: Env, seller: Address, sell_price: u32, buy_price: u32) {
        if e.storage().has(&DataKey::Price) {
            panic!("price is already created");
        }
        let price = Price {
            seller,
            sell_price,
            buy_price,
        };
        e.storage().set(&DataKey::Price, &price);
    }

    // update price
    pub fn update(e: Env, seller: Address, sell_price: u32, buy_price: u32) {
        if !e.storage().has(&DataKey::Price) {
            panic!("price is not created");
        }
        let price = Price {
            seller,
            sell_price,
            buy_price,
        };
        e.storage().set(&DataKey::Price, &price);
    }

    // get price
    pub fn get(e: Env) -> Price {
        if !e.storage().has(&DataKey::Price) {
            panic!("price is not created");
        }
        e.storage().get_unchecked(&DataKey::Price).unwrap()
    }

    // delete price
    pub fn delete(e: Env) {
        if !e.storage().has(&DataKey::Price) {
            panic!("price is deleted");
        }
        e.storage().remove(&DataKey::Price);
    }
}
// // getting price from oracle
// pub fn get_price(e: &Env) -> Price {
//     e.storage().get_unchecked(&DataKey::Price).unwrap()
// }

// // setting price in oracle
// pub fn set_price(e: &Env, price: &Price) {
//     e.storage().set(&DataKey::Price, price);
// }

mod test;
