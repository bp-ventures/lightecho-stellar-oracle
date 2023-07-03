#![cfg(test)]

use crate::{v2::Asset, v2::Oracle, v2::OracleClient};
use soroban_sdk::{testutils::Address as _, Address, Env};
extern crate std;

#[test]
fn test_initialize() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
fn test_admin() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.admin(), admin);
}

#[test]
fn test_sources() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.admin(), admin);
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let mut source: u32 = 2;
    env.mock_all_auths();
    client.add_price(&source, &asset1, &price1);
    let sources = client.sources();
    assert_eq!(sources.len(), 1);
    for s in sources.iter_unchecked() {
        assert_eq!(s, 2);
    }
    source = 3;
    client.add_price(&source, &asset2, &price2);
    let sources = client.sources();
    assert_eq!(sources.len(), 2);
    for (index_usize, s) in sources.iter_unchecked().enumerate() {
        let index: u32 = index_usize.try_into().unwrap();
        if index == 0 {
            assert_eq!(s, 2);
        } else if index == 1 {
            assert_eq!(s, 3);
        }
    }
}

#[test]
fn test_lastprices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let source = 0;
    let asset = Asset::Stellar(Address::random(&env));
    let price: i128 = 918729481812938171823918237122;
    client.add_price(&source, &asset, &price);
    client.add_price(&source, &asset, &price);
    client.add_price(&source, &asset, &price);
    client.add_price(&source, &asset, &price);

    let prices = client.lastprices(&asset, &10);
    assert_eq!(prices.len(), 4);
    for _p in prices.iter() {
        let p = _p.unwrap();
        assert_eq!(p.price, price);
        break;
    }
}

#[test]
fn test_lastprice() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset = Asset::Stellar(Address::random(&env));
    let price: i128 = 12345678;
    let source: u32 = 0;
    client.add_price(&source, &asset, &price);
    let lastprice = client.lastprice(&asset);
    assert_eq!(lastprice.unwrap().price, price);
}

#[test]
fn test_lastprice_two_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset1 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let price2: i128 = 2468;
    let source: u32 = 0;
    client.add_price(&source, &asset1, &price1);
    let mut lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price1);
    client.add_price(&source, &asset1, &price2);
    lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price2);
}

#[test]
fn test_lastprice_two_assets() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset1 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let asset2 = Asset::Stellar(Address::random(&env));
    let price2: i128 = 2468;
    let source: u32 = 0;
    client.add_price(&source, &asset1, &price1);
    client.add_price(&source, &asset2, &price2);
    let lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price1);
    let lastprice2 = client.lastprice(&asset2);
    assert_eq!(lastprice2.unwrap().price, price2);
}

#[test]
fn test_lastprice_multiple_sources_assets_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let source1: u32 = 0;
    let source2: u32 = 1;
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let asset3 = Asset::Stellar(Address::random(&env));
    let asset4 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 912794;
    let price2: i128 = 76123918273;
    let price3: i128 = 871982739102837;
    let price4: i128 = 12039812309182;
    let price5: i128 = 9192837192837;
    let price6: i128 = 182;
    let price7: i128 = 1;
    let price8: i128 = 907812630891721023980129383;

    client.add_price(&source1, &asset1, &price1);
    let mut lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price1);

    client.add_price(&source1, &asset1, &price2);
    client.add_price(&source1, &asset2, &price3);
    lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price2);
    lastprice = client.lastprice(&asset2);
    assert_eq!(lastprice.unwrap().price, price3);

    client.add_price(&source2, &asset2, &price4);
    lastprice = client.lastprice_by_source(&source2, &asset2);
    assert_eq!(lastprice.unwrap().price, price4);

    client.add_price(&source2, &asset3, &price5);
    client.add_price(&source2, &asset3, &price6);
    client.add_price(&source2, &asset4, &price7);
    client.add_price(&source2, &asset4, &price8);
    lastprice = client.lastprice_by_source(&source2, &asset3);
    assert_eq!(lastprice.unwrap().price, price6);
    lastprice = client.lastprice_by_source(&source2, &asset4);
    assert_eq!(lastprice.unwrap().price, price8);
}

#[test]
#[should_panic]
fn test_initialize_bad_auth() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
fn test_initialize_auth() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    env.mock_all_auths();
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
fn test_base() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.base(), base);
}

#[test]
fn test_assets() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.admin(), admin);
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let mut source: u32 = 2;
    env.mock_all_auths();
    client.add_price(&source, &asset1, &price1);
    let mut assets = client.assets();
    assert_eq!(assets.len(), 1);
    for a in assets.iter_unchecked() {
        assert_eq!(a, asset1);
    }
    source = 3;
    client.add_price(&source, &asset2, &price2);
    assets = client.assets();
    assert_eq!(assets.len(), 2);
    for (index_usize, a) in assets.iter_unchecked().enumerate() {
        let index: u32 = index_usize.try_into().unwrap();
        if index == 0 {
            assert_eq!(a, asset1);
        } else if index == 1 {
            assert_eq!(a, asset2);
        }
    }
}

#[test]
fn test_decimals() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.decimals(), decimals);
}

#[test]
fn test_resolution() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.resolution(), resolution);
}

#[test]
fn test_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let source = 0;
    let asset = Asset::Stellar(Address::random(&env));
    let price: i128 = 918729481812938171823918237122;
    client.add_price(&source, &asset, &price);

    let start_timestamp = env.ledger().timestamp() + 2;
    let end_timestamp = env.ledger().timestamp() + 3;
    let prices = client.prices(&asset, &start_timestamp, &end_timestamp);
    assert_eq!(prices.len(), 0);

    let start_timestamp = env.ledger().timestamp();
    let end_timestamp = start_timestamp;
    let prices = client.prices(&asset, &start_timestamp, &end_timestamp);
    assert_eq!(prices.len(), 1);
    for _p in prices.iter() {
        let p = _p.unwrap();
        assert_eq!(p.price, price);
        break;
    }

    let start_timestamp = env.ledger().timestamp();
    let end_timestamp = start_timestamp;
    let prices = client.prices_by_source(&0, &asset, &start_timestamp, &end_timestamp);
    assert_eq!(prices.len(), 1);
    for _p in prices.iter() {
        let p = _p.unwrap();
        assert_eq!(p.price, price);
        break;
    }
}
