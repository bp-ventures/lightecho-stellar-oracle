use soroban_sdk::contracttype;

pub(crate) const ONE_MINUTE_IN_LEDGERS: u32 = 12;
pub(crate) const DAY_IN_LEDGERS: u32 = 17280;

pub(crate) const TEMPORARY_BUMP_AMOUNT: u32 = 10 * ONE_MINUTE_IN_LEDGERS;
pub(crate) const TEMPORARY_LIFETIME_THRESHOLD: u32 = TEMPORARY_BUMP_AMOUNT - ONE_MINUTE_IN_LEDGERS;

pub(crate) const PERSISTENT_BUMP_AMOUNT: u32 = 30 * DAY_IN_LEDGERS;
pub(crate) const PERSISTENT_LIFETIME_THRESHOLD: u32 = PERSISTENT_BUMP_AMOUNT - DAY_IN_LEDGERS;

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
