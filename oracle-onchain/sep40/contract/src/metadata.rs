use crate::storage_types::{bump_instance, Asset, DataKey};
use soroban_sdk::{Address, Env};

pub fn has_admin(env: &Env) -> bool {
    let key = DataKey::Admin;
    if let Some(_) = env.storage().persistent().get::<DataKey, i128>(&key) {
        bump_instance(env);
        return true;
    } else {
        return false;
    }
}

pub fn read_admin(env: &Env) -> Address {
    let key = DataKey::Admin;
    bump_instance(env);
    return env.storage().persistent().get(&key).unwrap();
}

pub fn write_admin(env: &Env, id: &Address) {
    env.storage().persistent().set(&DataKey::Admin, id);
    bump_instance(env);
}

pub fn write_base(env: &Env, base: &Asset) {
    env.storage().persistent().set(&DataKey::Base, base);
}

pub fn read_base(env: &Env) -> Asset {
    return env.storage().persistent().get(&DataKey::Base).unwrap();
}

pub fn write_decimals(env: &Env, decimals: &u32) {
    env.storage().persistent().set(&DataKey::Decimals, decimals);
}

pub fn read_decimals(env: &Env) -> u32 {
    return env.storage().persistent().get(&DataKey::Decimals).unwrap();
}

pub fn write_resolution(env: &Env, resolution: &u32) {
    env.storage()
        .persistent()
        .set(&DataKey::Resolution, resolution);
}

pub fn read_resolution(env: &Env) -> u32 {
    return env
        .storage()
        .persistent()
        .get(&DataKey::Resolution)
        .unwrap();
}

pub fn write_metadata(env: &Env, admin: &Address, base: &Asset, decimals: &u32, resolution: &u32) {
    write_admin(env, admin);
    write_base(env, base);
    write_decimals(env, decimals);
    write_resolution(env, resolution);
}
