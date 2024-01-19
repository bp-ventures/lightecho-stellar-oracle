#![no_std]

mod constants;
mod types;
mod utils;

#[cfg(feature = "use_map")]
mod contract_map;
#[cfg(feature = "use_map")]
mod test_map;

#[cfg(feature = "use_light")]
mod contract_light;
#[cfg(feature = "use_light")]
mod test_light;
