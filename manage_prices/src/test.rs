#![cfg(test)]

#[test]
fn it_works() {
    let mut env = Env::default();
    set_price(&env, 100);
    assert_eq!(get_price(env), 100);
}
