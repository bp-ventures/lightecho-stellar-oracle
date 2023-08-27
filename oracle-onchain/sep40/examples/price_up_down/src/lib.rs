#![no_std]

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}
mod contract;
mod storage_types;
mod metadata;
mod test;
