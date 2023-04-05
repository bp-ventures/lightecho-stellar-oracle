use soroban_sdk::{contractimpl, contracttype, xdr::AccountId, Env};

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Price,
}

pub struct Price {
    pub seller: AccountId,
    pub sell_price: u32,
    pub buy_price: u32,
}

pub struct PriceUpdate;

#[contractimpl]
impl PriceUpdate {
    // setting price in oracle
    pub fn set_price(e: &Env, price: &Price) {
        e.storage().set(&DataKey::Price, price);
    }

    // getting price from oracle
    pub fn get_price(e: Env) -> Price {
        e.storage().get_unchecked(&DataKey::Price).unwrap()
    }
}

mod test;
