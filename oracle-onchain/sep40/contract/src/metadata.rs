use crate::storage_types::{Asset, DataKey};
use soroban_sdk::{Address, Env};

pub fn has_admin(env: &Env) -> bool {
    let key = DataKey::Admin;
    let admin_option: Option<Address> = env.storage().instance().get(&key);
    match admin_option {
        Some(_) => { return true }
        None => { return false }
    }
}

pub fn read_admin(env: &Env) -> Address {
    let key = DataKey::Admin;
    return env.storage().instance().get(&key).unwrap();
}

pub fn write_admin(env: &Env, id: &Address) {
    env.storage().instance().set(&DataKey::Admin, id);
}

pub fn write_base(env: &Env, base: &Asset) {
    env.storage().instance().set(&DataKey::Base, base);
}

pub fn read_base(env: &Env) -> Asset {
    return env.storage().instance().get(&DataKey::Base).unwrap();
}

pub fn write_decimals(env: &Env, decimals: &u32) {
    env.storage().instance().set(&DataKey::Decimals, decimals);
}

pub fn read_decimals(env: &Env) -> u32 {
    return env.storage().instance().get(&DataKey::Decimals).unwrap();
}

pub fn write_resolution(env: &Env, resolution: &u32) {
    env.storage()
        .instance()
        .set(&DataKey::Resolution, resolution);
}

pub fn read_resolution(env: &Env) -> u32 {
    return env
        .storage()
        .instance()
        .get(&DataKey::Resolution)
        .unwrap();
}

pub fn write_metadata(env: &Env, admin: &Address, base: &Asset, decimals: &u32, resolution: &u32) {
    write_admin(env, admin);
    write_base(env, base);
    write_decimals(env, decimals);
    write_resolution(env, resolution);
}
