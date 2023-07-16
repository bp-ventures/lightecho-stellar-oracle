use crate::storage_types::{Asset, DataKey, PERSISTENT_BUMP_AMOUNT};
use soroban_sdk::{Address, Env};

pub fn has_admin(env: &Env) -> bool {
    return env.storage().instance().has(&DataKey::Admin);
}

pub fn read_admin(env: &Env) -> Address {
    return env.storage().instance().get(&DataKey::Admin).unwrap();
}

pub fn write_admin(env: &Env, id: &Address) {
    return env.storage().instance().set(&DataKey::Admin, id);
}

pub fn write_base(env: &Env, base: &Asset) {
    let key = DataKey::Base;
    env.storage().persistent().set(&key, base);
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
}

pub fn read_base(env: &Env) -> Asset {
    let key = DataKey::Base;
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
    return env.storage().persistent().get(&key).unwrap();
}

pub fn write_decimals(env: &Env, decimals: &u32) {
    let key = DataKey::Decimals;
    env.storage().persistent().set(&key, decimals);
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
}

pub fn read_decimals(env: &Env) -> u32 {
    let key = DataKey::Decimals;
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
    return env.storage().persistent().get(&key).unwrap();
}

pub fn write_resolution(env: &Env, resolution: &u32) {
    let key = DataKey::Resolution;
    env.storage().persistent().set(&key, resolution);
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
}

pub fn read_resolution(env: &Env) -> u32 {
    let key = DataKey::Resolution;
    env.storage()
        .persistent()
        .bump(&key, PERSISTENT_BUMP_AMOUNT);
    return env.storage().persistent().get(&key).unwrap();
}

pub fn write_metadata(env: &Env, admin: &Address, base: &Asset, decimals: &u32, resolution: &u32) {
    write_admin(env, admin);
    write_base(env, base);
    write_decimals(env, decimals);
    write_resolution(env, resolution);
}
