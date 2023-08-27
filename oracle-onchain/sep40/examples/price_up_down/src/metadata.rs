use crate::storage_types::{DataKey, PERSISTENT_BUMP_AMOUNT};
use soroban_sdk::{Address, Env};

pub fn write_oracle_contract_id(env: &Env, oracle_contract_id: &Address) {
    let key = DataKey::OracleContractId;
    env.storage().persistent().set(&key, oracle_contract_id);
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
}

pub fn read_oracle_contract_id(env: &Env) -> Address {
    let key = DataKey::OracleContractId;
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
    return env.storage().persistent().get(&key).unwrap();
}

pub fn has_oracle_contract_id(env: &Env) -> bool {
    return env.storage().instance().has(&DataKey::OracleContractId);
}

pub fn write_metadata(env: &Env, oracle_contract_id: &Address) {
    write_oracle_contract_id(env, oracle_contract_id);
}
