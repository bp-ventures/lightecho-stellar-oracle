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
    pub fn create(e: Env, seller: AccountId, sell_price: u32, buy_price: u32) {
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

    pub fn update(e: Env, seller: AccountId, sell_price: u32, buy_price: u32) {
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
}
// getting price from oracle
pub fn get_price(e: &Env) -> Price {
    e.storage().get_unchecked(&DataKey::Price).unwrap()
}

// setting price in oracle
pub fn set_price(e: &Env, price: &Price) {
    e.storage().set(&DataKey::Price, price);
}

mod test;
