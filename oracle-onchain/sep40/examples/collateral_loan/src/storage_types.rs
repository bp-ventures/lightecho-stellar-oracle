use soroban_sdk::{contracttype, Address, Symbol};

pub(crate) const TEMPORARY_BUMP_AMOUNT: u32 = 17280; // 1 day
pub(crate) const INSTANCE_BUMP_AMOUNT: u32 = 34560; // 2 days
pub(crate) const PERSISTENT_BUMP_AMOUNT: u32 = 518400; // 30 days

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub enum Asset {
    Stellar(Address),
    Other(Symbol),
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub struct Info {
    pub loan_available_principal: bool,
    pub collateral_asset: Asset,
    pub collateral_rate: i128,
    pub collateral_termination_rate: i128,
}

#[derive(Clone, PartialEq, Debug)]
#[contracttype]
pub struct Request {
    pub memo: Symbol,
}
