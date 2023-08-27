use soroban_sdk::{contracttype, Address, Symbol};

pub(crate) const TEMPORARY_BUMP_AMOUNT: u32 = 17280; // 1 day
pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 34560; // 2 days
pub(crate) const PERSISTENT_BUMP_AMOUNT: u32 = 518400; // 30 days

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
