# Rust/Wasm ERC20 Contract

This directory contains a Rust implementation of an ERC20 contract that is compiled into Wasm.

As is the case with many chains that use Wasm contracts, we compile this Rust project as a library;
that way, functions referenced in external libraries become host functions which can be provided via Wasm module imports.

In order to reduce the 
