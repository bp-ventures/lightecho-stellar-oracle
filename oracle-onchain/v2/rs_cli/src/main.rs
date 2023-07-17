use soroban_sdk::{testutils::Address as _, Address, Env};

mod oracle {
    soroban_sdk::contractimport!(
        file = "../../contract/target/wasm32-unknown-unknown/release/oracle.wasm"
    );
}

fn main() {
    let env = Env::default();
    let contract_address = Address::from_val(env, &config.token_contract_id)
    let oracle_id = env.register_contract_wasm(None, oracle::WASM);
    let client = oracle::Client::new(&env, &oracle_id);
    client.initialize(
        &Address::random(&env),
        &oracle::Asset::Stellar(Address::random(&env)),
        &18,
        &60,
    );
}
