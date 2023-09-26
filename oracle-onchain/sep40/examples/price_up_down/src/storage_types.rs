use soroban_sdk::{contracttype, Env};

pub(crate) const DAY_IN_LEDGERS: u32 = 17280;

pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 7 * DAY_IN_LEDGERS;
pub(crate) const INSTANCE_LIFETIME_THRESHOLD: u32 = INSTANCE_BUMP_AMOUNT - DAY_IN_LEDGERS;

#[derive(Clone, Copy)]
#[contracttype]
pub enum DataKey {
    OracleContractId = 0,
    Prices = 1,
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub struct UpDown {
    pub up: bool,
    pub down: bool,
    pub equal: bool,
}

pub fn bump_instance(env: &Env) {
    env.storage()
        .instance()
        .bump(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}
