use soroban_sdk::{contracttype, Env};

pub(crate) const ONE_MINUTE_IN_LEDGERS: u32 = 12;
pub(crate) const DAY_IN_LEDGERS: u32 = 17280;

pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 7 * DAY_IN_LEDGERS;
pub(crate) const INSTANCE_LIFETIME_THRESHOLD: u32 = INSTANCE_BUMP_AMOUNT - DAY_IN_LEDGERS;

pub(crate) const TEMPORARY_BUMP_AMOUNT: u32 = 10 * ONE_MINUTE_IN_LEDGERS;
pub(crate) const TEMPORARY_LIFETIME_THRESHOLD: u32 = TEMPORARY_BUMP_AMOUNT - ONE_MINUTE_IN_LEDGERS;

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

pub fn bump_temporary(env: &Env, key: &DataKey) {
    env.storage()
        .temporary()
        .bump(key, TEMPORARY_LIFETIME_THRESHOLD, TEMPORARY_BUMP_AMOUNT);
}

pub fn bump_instance(env: &Env) {
    env.storage()
        .instance()
        .bump(INSTANCE_LIFETIME_THRESHOLD, INSTANCE_BUMP_AMOUNT);
}
