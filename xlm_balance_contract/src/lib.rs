#![no_std]

use soroban_sdk::{contractimpl, contracttype, Address, Env};

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Balance,
}

#[derive(Clone)]
#[contracttype]
pub struct Balance {
    pub owner: Address,
    pub amount: u32,
}

pub struct BalanceContract;

#[contractimpl]
impl BalanceContract {
    // get balance
    pub fn get(e: Env) -> Balance {
        if !e.storage().has(&DataKey::Balance) {
            panic!("no balance found");
        }

        e.storage().get_unchecked(&DataKey::Balance).unwrap()
    }
}

mod test;
