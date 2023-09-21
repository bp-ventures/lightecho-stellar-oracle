use crate::storage_types::{bump_instance, DataKey};
use soroban_sdk::{Address, Env};

pub fn write_oracle_contract_id(env: &Env, oracle_contract_id: &Address) {
    let key = DataKey::OracleContractId;
    env.storage().instance().set(&key, oracle_contract_id);
    bump_instance(env);
}

pub fn read_oracle_contract_id(env: &Env) -> Address {
    let key = DataKey::OracleContractId;
    bump_instance(env);
    return env.storage().instance().get(&key).unwrap();
}

pub fn has_oracle_contract_id(env: &Env) -> bool {
    let key = DataKey::OracleContractId;
    if let Some(_) = env.storage().instance().get::<DataKey, i128>(&key) {
        bump_instance(env);
        return true;
    } else {
        return false;
    }
}

pub fn write_metadata(env: &Env, oracle_contract_id: &Address) {
    write_oracle_contract_id(env, oracle_contract_id);
}
