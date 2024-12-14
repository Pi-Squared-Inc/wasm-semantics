#!/bin/bash
LOC_FLAG="-Zlocation-detail=none" # removes debugging info from binary
FMT_FLAG="-Zfmt-debug=none"       # removes formatter code from binary
RUSTFLAGS="$LOC_FLAG $FMT_FLAG" cargo +nightly build --release --target wasm32-unknown-unknown \
-Z build-std=std,panic_abort \
-Z build-std-features="optimize_for_size,panic_immediate_abort"
