#![cfg(test)]

use crate::contract::{Oracle, OracleClient};
use crate::storage_types::{Asset, Price};
use soroban_sdk::{testutils::Address as _, Address, BytesN, Env, Vec};
extern crate std;

fn is_asset_in_vec(asset: Asset, vec: &Vec<Asset>) -> bool {
    for item in vec.iter() {
        if item == asset {
            return true;
        }
    }
    return false;
}

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
#[should_panic]
fn test_initialize_twice() {
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
fn test_admin() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.read_admin(), admin);
}

#[test]
fn test_has_admin() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    assert_eq!(client.has_admin(), false);
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.has_admin(), true);
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
    assert_eq!(client.read_admin(), admin);
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let mut source: u32 = 2;
    let timestamp1 = env.ledger().timestamp();
    let timestamp2 = env.ledger().timestamp() + 1;
    env.mock_all_auths();
    client.add_price(&source, &asset1, &price1, &timestamp1);
    let sources = client.sources();
    assert_eq!(sources.len(), 1);
    for s in sources.iter() {
        assert_eq!(s, 2);
    }
    source = 3;
    client.add_price(&source, &asset2, &price2, &timestamp2);
    let sources = client.sources();
    assert_eq!(sources.len(), 2);
    for (index_usize, s) in sources.iter().enumerate() {
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);

    let prices = client.prices(&asset, &10);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 4);
    for p in prices.iter() {
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset, &price, &timestamp);
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset1, &price1, &timestamp);
    let mut lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price1);
    client.add_price(&source, &asset1, &price2, &timestamp);
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset1, &price1, &timestamp);
    client.add_price(&source, &asset2, &price2, &timestamp);
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
    let timestamp = env.ledger().timestamp();

    client.add_price(&source1, &asset1, &price1, &timestamp);
    let mut lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price1);

    client.add_price(&source1, &asset1, &price2, &timestamp);
    client.add_price(&source1, &asset2, &price3, &timestamp);
    lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price2);
    lastprice = client.lastprice(&asset2);
    assert_eq!(lastprice.unwrap().price, price3);

    client.add_price(&source2, &asset2, &price4, &timestamp);
    lastprice = client.lastprice_by_source(&source2, &asset2);
    assert_eq!(lastprice.unwrap().price, price4);

    client.add_price(&source2, &asset3, &price5, &timestamp);
    client.add_price(&source2, &asset3, &price6, &timestamp);
    client.add_price(&source2, &asset4, &price7, &timestamp);
    client.add_price(&source2, &asset4, &price8, &timestamp);
    lastprice = client.lastprice_by_source(&source2, &asset3);
    assert_eq!(lastprice.unwrap().price, price6);
    lastprice = client.lastprice_by_source(&source2, &asset4);
    assert_eq!(lastprice.unwrap().price, price8);
}

#[test]
fn test_remove_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let source0: u32 = 0;
    let source1: u32 = 1;
    let source2: u32 = 2;
    let asset0 = Asset::Stellar(Address::random(&env));
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let asset3 = Asset::Stellar(Address::random(&env));
    let price0: i128 = 912794;
    let price1: i128 = 76123918273;
    let price2: i128 = 871982739102837;
    let price3: i128 = 12039812309182;
    let price4: i128 = 9192837192837;
    let price5: i128 = 182;
    let price6: i128 = 1;
    let price7: i128 = 907812630891721023980129383;
    let timestamp = env.ledger().timestamp();

    client.add_price(&source0, &asset0, &price0, &timestamp);
    let mut lastprice = client.lastprice(&asset0);
    assert_eq!(lastprice.unwrap().price, price0);

    client.add_price(&source0, &asset0, &price1, &timestamp);
    client.add_price(&source0, &asset1, &price2, &timestamp);
    lastprice = client.lastprice(&asset0);
    assert_eq!(lastprice.unwrap().price, price1);
    lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price2);

    client.add_price(&source1, &asset1, &price3, &timestamp);
    lastprice = client.lastprice_by_source(&source1, &asset1);
    assert_eq!(lastprice.unwrap().price, price3);

    client.add_price(&source1, &asset2, &price4, &timestamp);
    client.add_price(&source1, &asset2, &price5, &timestamp);
    client.add_price(&source1, &asset3, &price6, &timestamp);
    client.add_price(&source1, &asset3, &price7, &timestamp);
    lastprice = client.lastprice_by_source(&source1, &asset2);
    assert_eq!(lastprice.unwrap().price, price5);
    lastprice = client.lastprice_by_source(&source1, &asset3);
    assert_eq!(lastprice.unwrap().price, price7);

    let start_timestamp: Option<u64> = None;
    let end_timestamp: Option<u64> = None;

    client.remove_prices(
        &Vec::<u32>::from_array(&env, [0]),
        &Vec::<Asset>::from_array(&env, [asset0.clone()]),
        &start_timestamp,
        &end_timestamp,
    );

    lastprice = client.lastprice_by_source(&source0, &asset1);
    assert_eq!(lastprice.unwrap().price, price2);
    let assets = client.assets();
    assert_eq!(assets.len(), 3);
    assert_eq!(is_asset_in_vec(asset1.clone(), &assets), true);
    assert_eq!(is_asset_in_vec(asset2.clone(), &assets), true);
    assert_eq!(is_asset_in_vec(asset3.clone(), &assets), true);

    client.remove_prices(
        &Vec::<u32>::from_array(&env, []),
        &Vec::<Asset>::from_array(&env, [asset1.clone()]),
        &start_timestamp,
        &end_timestamp,
    );

    let sources = client.sources();
    assert_eq!(sources.len(), 1);
    for s in sources.iter() {
        if s != source1 {
            panic!("unexpected source")
        }
    }

    let timestamp = env.ledger().timestamp();
    client.add_price(&source0, &asset0, &price1, &timestamp);
    client.add_price(&source2, &asset1, &price2, &timestamp);

    let assets = client.assets();
    assert_eq!(assets.len(), 4);
    assert_eq!(is_asset_in_vec(asset0.clone(), &assets), true);
    assert_eq!(is_asset_in_vec(asset1.clone(), &assets), true);
    assert_eq!(is_asset_in_vec(asset2.clone(), &assets), true);
    assert_eq!(is_asset_in_vec(asset3.clone(), &assets), true);
    let sources = client.sources();
    assert_eq!(sources.len(), 3);
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
    assert_eq!(client.read_admin(), admin);
    let asset1 = Asset::Stellar(Address::random(&env));
    let asset2 = Asset::Stellar(Address::random(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let timestamp = env.ledger().timestamp();
    let mut source: u32 = 2;
    env.mock_all_auths();
    client.add_price(&source, &asset1, &price1, &timestamp);
    let mut assets = client.assets();
    assert_eq!(assets.len(), 1);
    for a in assets.iter() {
        assert_eq!(a, asset1);
    }
    source = 3;
    client.add_price(&source, &asset2, &price2, &timestamp);
    assets = client.assets();
    assert_eq!(assets.len(), 2);
    assert_eq!(is_asset_in_vec(asset1, &assets), true);
    assert_eq!(is_asset_in_vec(asset2, &assets), true);
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset, &price, &timestamp);

    let prices = client.prices(&asset, &1);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 1);

    let price: i128 = 71821892379218;
    let timestamp = timestamp + 1;
    client.add_price(&source, &asset, &price, &timestamp);
    let prices = client.prices(&asset, &5);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 2);
}

#[test]
fn test_prices_limit() {
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
    let timestamp = env.ledger().timestamp();
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);

    let prices = client.prices_by_source(&source, &asset, &5);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 5);
    let prices = client.prices_by_source(&source, &asset, &10);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 10);
    let prices = client.prices_by_source(&source, &asset, &15);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 10);

    client.add_price(&source, &asset, &price, &timestamp);
    let prices = client.prices_by_source(&source, &asset, &15);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 10);

    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);
    client.add_price(&source, &asset, &price, &timestamp);

    client.add_price(&source, &asset, &price, &timestamp);
    let prices = client.prices_by_source(&source, &asset, &3);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 3);
    let prices = client.prices_by_source(&source, &asset, &30);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 10);
}

#[test]
fn test_add_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let mut prices = Vec::<Price>::new(&env);
    let source0 = 0;
    let asset0_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset0_address = Address::from_contract_id(&asset0_bytes);
    let asset0 = Asset::Stellar(asset0_address);
    let price0: i128 = 918729481812938171823918237122;
    let timestamp0 = env.ledger().timestamp();
    prices.push_back(Price {
        source: source0,
        asset: asset0,
        price: price0,
        timestamp: timestamp0,
    });
    let source1 = 0;
    let asset1_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset1_address = Address::from_contract_id(&asset1_bytes);
    let asset1 = Asset::Stellar(asset1_address);
    let price1: i128 = 918729481812938171823918237123;
    let timestamp1 = timestamp0 + 1;
    prices.push_back(Price {
        source: source1,
        asset: asset1,
        price: price1,
        timestamp: timestamp1,
    });
    client.add_prices(&prices);
    let asset3_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset3_address = Address::from_contract_id(&asset3_bytes);
    let asset3 = Asset::Stellar(asset3_address);
    let prices = client.prices_by_source(&0, &asset3, &5);
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 2);
}

#[test]
fn test_get_all_lastprices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let mut prices = Vec::<Price>::new(&env);
    let source0 = 0;
    let asset0_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset0_address = Address::from_contract_id(&asset0_bytes);
    let asset0 = Asset::Stellar(asset0_address);
    let price0: i128 = 918729481812938171823918237122;
    let timestamp0 = env.ledger().timestamp();
    prices.push_back(Price {
        source: source0,
        asset: asset0,
        price: price0,
        timestamp: timestamp0,
    });
    let source1 = 0;
    let asset1_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset1_address = Address::from_contract_id(&asset1_bytes);
    let asset1 = Asset::Stellar(asset1_address);
    let price1: i128 = 918729481812938171823918237123;
    let timestamp1 = timestamp0 + 1;
    prices.push_back(Price {
        source: source1,
        asset: asset1,
        price: price1,
        timestamp: timestamp1,
    });
    client.add_prices(&prices);
    let asset3_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset3_address = Address::from_contract_id(&asset3_bytes);
    let asset3 = Asset::Stellar(asset3_address);
    let prices = client.prices_by_source(&0, &asset3, &5);
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 2);

    let asset4_bytes = BytesN::from_array(&env, &[8; 32]);
    let asset4_address = Address::from_contract_id(&asset4_bytes);
    let asset4 = Asset::Stellar(asset4_address);

    let all_lastprices = client.get_all_lastprices(&source0);
    assert_eq!(all_lastprices.keys().len(), 1);
    assert_eq!(all_lastprices.get(asset4).unwrap().len(), 1);
}

#[test]
#[should_panic]
fn test_write_admin_without_initialize() {
    let env = Env::default();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    client.write_admin(&admin);
}

#[test]
fn test_write_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, Oracle);
    let client = OracleClient::new(&env, &contract_id);
    let admin = Address::random(&env);
    let base = Asset::Stellar(Address::random(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let existing_admin = client.read_admin();
    assert_eq!(admin, existing_admin);
    let admin2 = Address::random(&env);
    client.write_admin(&admin2);
    let new_admin = client.read_admin();
    assert_eq!(admin2, new_admin);
}
