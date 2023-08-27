#![no_std]

use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, Symbol};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

#[contract]
pub struct CollateralLoan;

#[contractimpl]
impl CollateralLoan {
    pub fn info(env: Env) -> Info {
        return Info {
            loan_available_principal: true,
            collateral_asset: Asset::Other(Symbol::new(&env, "USD")),
            collateral_rate: 2,
            collateral_termination_rate: 1,
        };
    }

    pub fn request(env: Env) -> Request {}
}

mod test;
