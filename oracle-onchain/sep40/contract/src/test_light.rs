#![cfg(test)]

use crate::contract_light::{LightOracle, LightOracleClient};
use crate::types::{Asset, InternalPrice};
use soroban_sdk::{testutils::Address as _, Address, Env, Vec};
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
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
#[should_panic]
fn test_initialize_bad_auth() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
#[should_panic]
fn test_initialize_twice() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    env.mock_all_auths();
    client.initialize(&admin, &base, &decimals, &resolution);
}

#[test]
fn test_admin() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.read_admin().unwrap(), admin);
}

#[test]
fn test_sources() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.read_admin().unwrap(), admin);
    let asset1 = Asset::Stellar(Address::generate(&env));
    let asset2 = Asset::Stellar(Address::generate(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let mut source: u32 = 2;
    let timestamp1 = env.ledger().timestamp();
    let timestamp2 = env.ledger().timestamp() + 1;
    env.mock_all_auths();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price1,
        timestamp: timestamp1,
    });
    client.add_prices(&prices);
    let sources = client.sources();
    assert_eq!(sources.len(), 1);
    for s in sources.iter() {
        assert_eq!(s, 2);
    }
    source = 3;
    prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price2,
        timestamp: timestamp2,
    });
    client.add_prices(&prices);
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
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;

    client.initialize(&admin, &base, &decimals, &resolution);

    let source = 0;
    let asset = Asset::Stellar(Address::generate(&env));
    let price: i128 = 918729481812938171823918237122;
    let timestamp = env.ledger().timestamp();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);

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
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset = Asset::Stellar(Address::generate(&env));
    let price: i128 = 12345678;
    let source: u32 = 0;
    let timestamp = env.ledger().timestamp();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);
    let lastprice = client.lastprice(&asset);
    assert_eq!(lastprice.unwrap().price, price);
}

#[test]
fn test_lastprice_two_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset1 = Asset::Stellar(Address::generate(&env));
    let price1: i128 = 13579;
    let price2: i128 = 2468;
    let source: u32 = 0;
    let timestamp = env.ledger().timestamp();

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price1,
        timestamp,
    });
    client.add_prices(&prices);
    let mut lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price1);
    prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price2,
        timestamp,
    });
    client.add_prices(&prices);
    lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price2);
}

#[test]
fn test_lastprice_two_assets() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let asset1 = Asset::Stellar(Address::generate(&env));
    let price1: i128 = 13579;
    let asset2 = Asset::Stellar(Address::generate(&env));
    let price2: i128 = 2468;
    let source: u32 = 0;
    let timestamp = env.ledger().timestamp();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price1,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price2,
        timestamp,
    });
    client.add_prices(&prices);
    let lastprice1 = client.lastprice(&asset1);
    assert_eq!(lastprice1.unwrap().price, price1);
    let lastprice2 = client.lastprice(&asset2);
    assert_eq!(lastprice2.unwrap().price, price2);
}

#[test]
fn test_lastprice_multiple_sources_assets_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let source1: u32 = 0;
    let source2: u32 = 1;
    let asset1 = Asset::Stellar(Address::generate(&env));
    let asset2 = Asset::Stellar(Address::generate(&env));
    let asset3 = Asset::Stellar(Address::generate(&env));
    let asset4 = Asset::Stellar(Address::generate(&env));
    let price1: i128 = 912794;
    let price2: i128 = 76123918273;
    let price3: i128 = 871982739102837;
    let price4: i128 = 12039812309182;
    let price5: i128 = 9192837192837;
    let price6: i128 = 182;
    let price7: i128 = 1;
    let price8: i128 = 907812630891721023980129383;
    let timestamp = env.ledger().timestamp();

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source: source1,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price1,
        timestamp,
    });
    client.add_prices(&prices);
    let mut lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price1);

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source: source1,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price2,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source: source1,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price3,
        timestamp,
    });
    client.add_prices(&prices);
    lastprice = client.lastprice(&asset1);
    assert_eq!(lastprice.unwrap().price, price2);
    lastprice = client.lastprice(&asset2);
    assert_eq!(lastprice.unwrap().price, price3);

    prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source: source2,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price4,
        timestamp,
    });
    client.add_prices(&prices);
    lastprice = client.lastprice_by_source(&source2, &asset2);
    assert_eq!(lastprice.unwrap().price, price4);

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source: source2,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price5,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source: source2,
        asset: asset3.clone(),
        asset_u32: 3,
        price: price6,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source: source2,
        asset: asset3.clone(),
        asset_u32: 3,
        price: price7,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source: source2,
        asset: asset4.clone(),
        asset_u32: 4,
        price: price8,
        timestamp,
    });
    lastprice = client.lastprice_by_source(&source2, &asset3);
    assert_eq!(lastprice.unwrap().price, price6);
    lastprice = client.lastprice_by_source(&source2, &asset4);
    assert_eq!(lastprice.unwrap().price, price8);
}

#[test]
fn test_base() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.base(), base);
}

#[test]
fn test_assets() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.read_admin().unwrap(), admin);
    let asset1 = Asset::Stellar(Address::generate(&env));
    let asset2 = Asset::Stellar(Address::generate(&env));
    let price1: i128 = 13579;
    let price2: i128 = 912739812;
    let timestamp = env.ledger().timestamp();
    let mut source: u32 = 2;
    env.mock_all_auths();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset1.clone(),
        asset_u32: 1,
        price: price1,
        timestamp,
    });
    client.add_prices(&prices);
    let mut assets = client.assets();
    assert_eq!(assets.len(), 1);
    for a in assets.iter() {
        assert_eq!(a, asset1);
    }
    source = 3;
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset2.clone(),
        asset_u32: 2,
        price: price2,
        timestamp,
    });
    client.add_prices(&prices);
    assets = client.assets();
    assert_eq!(assets.len(), 2);
    assert_eq!(is_asset_in_vec(asset1, &assets), true);
    assert_eq!(is_asset_in_vec(asset2, &assets), true);
}

#[test]
fn test_decimals() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.decimals(), decimals);
}

#[test]
fn test_resolution() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    assert_eq!(client.resolution(), resolution);
}

#[test]
fn test_prices() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let source = 0;
    let asset = Asset::Stellar(Address::generate(&env));
    let price: i128 = 918729481812938171823918237122;
    let timestamp = env.ledger().timestamp();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);

    let prices = client.prices(&asset, &1);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 1);

    let price: i128 = 71821892379218;
    let timestamp = timestamp + 1;
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);
    let prices = client.prices(&asset, &5);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 2);
}

#[test]
fn test_prices_limit() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let source = 0;
    let asset = Asset::Stellar(Address::generate(&env));
    let price: i128 = 918729481812938171823918237122;
    let timestamp = env.ledger().timestamp();
    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);

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

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);
    let prices = client.prices_by_source(&source, &asset, &15);
    assert!(!prices.is_none());
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 10);

    let mut prices = Vec::<InternalPrice>::new(&env);
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    prices.push_back(InternalPrice {
        source,
        asset: asset.clone(),
        asset_u32: 0,
        price,
        timestamp,
    });
    client.add_prices(&prices);
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
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);

    let mut prices = Vec::<InternalPrice>::new(&env);
    let source0 = 0;
    let asset0 = Asset::Stellar(Address::generate(&env));
    let price0: i128 = 918729481812938171823918237122;
    let timestamp0 = env.ledger().timestamp();
    prices.push_back(InternalPrice {
        source: source0,
        asset: asset0.clone(),
        asset_u32: 0,
        price: price0,
        timestamp: timestamp0,
    });
    let price1: i128 = 918729481812938171823918237123;
    let timestamp1 = timestamp0 + 1;
    prices.push_back(InternalPrice {
        source: source0,
        asset: asset0.clone(),
        asset_u32: 0,
        price: price1,
        timestamp: timestamp1,
    });
    client.add_prices(&prices);
    let prices = client.prices_by_source(&source0, &asset0, &5);
    let prices = prices.unwrap();
    assert_eq!(prices.len(), 2);
}

#[test]
#[should_panic]
fn test_write_admin_without_initialize() {
    let env = Env::default();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    client.write_admin(&admin);
}

#[test]
fn test_write_admin() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, LightOracle);
    let client = LightOracleClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let base = Asset::Stellar(Address::generate(&env));
    let decimals = 18;
    let resolution = 1;
    client.initialize(&admin, &base, &decimals, &resolution);
    let existing_admin = client.read_admin();
    assert_eq!(admin, existing_admin.unwrap());
    let admin2 = Address::generate(&env);
    client.write_admin(&admin2);
    let new_admin = client.read_admin();
    assert_eq!(admin2, new_admin.unwrap());
}
