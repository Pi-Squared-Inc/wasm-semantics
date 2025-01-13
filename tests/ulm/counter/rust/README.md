# Rust/Wasm Counter Contract

This directory contains a Rust implementation of an Counter contract that is compiled into Wasm.

As is the case with many chains that use Wasm contracts, we compile this Rust project as a library;
that way, functions referenced in external libraries become host functions which can be provided via Wasm module imports.

In order to reduce the size of the compiled Wasm library, we referred to this guide:

https://github.com/johnthagen/min-sized-rust

To build the contract with all of the size minimization options, first, ensure that a recent build of the Rust compiler is installed with the Wasm32 target, which can be done with:

```sh
rustup install nightly
rustup target add wasm32-unknown-unknown --toolchain nightly
rustup component add rust-src --toolchain nightly-x86_64-unknown-linux-gnu
```

Then run the build script as follows:

```sh
./build.sh
```
