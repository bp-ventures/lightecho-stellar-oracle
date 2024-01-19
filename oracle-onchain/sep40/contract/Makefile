default: build_light

all: test_light

test_light: build_light
	cargo test

test_map: build_map
	cargo test

build_light:
	cargo build --features="use_light" --target wasm32-unknown-unknown --release
	@ls -l target/wasm32-unknown-unknown/release/*.wasm

build_map:
	cargo build --features="use_map" --target wasm32-unknown-unknown --release
	@ls -l target/wasm32-unknown-unknown/release/*.wasm

fmt:
	cargo fmt --all

clean:
	cargo clean

