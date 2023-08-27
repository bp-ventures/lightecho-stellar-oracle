#![no_std]

use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, Symbol};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub enum Asset {
    Stellar(Address),
    Other(Symbol),
}

#[contracttype]
pub struct Info {
    pub loan_available_principal: bool,
    pub collateral_asset: Asset,
}

#[contract]
pub struct CollateralLoan;

#[contractimpl]
impl CollateralLoan {
    pub fn info(env: Env) {}
}

mod test;
