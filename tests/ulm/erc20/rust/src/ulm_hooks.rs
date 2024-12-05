use bytes::{Bytes, Buf};

use crate::unsigned::U256;

extern "C" {
    #[allow(dead_code)]
    pub fn fail(msg: *const u8, msg_len: usize) -> !;

    // result must have a length of exactly 32.
    pub fn keccakHash(msg: *const u8, msg_len: usize, result: *mut u8);
}

#[cfg(test)]
pub mod overrides {
    #[no_mangle]
    pub extern "C" fn fail(_msg: *const u8, _msg_len: usize) -> ! {
        panic!("fail called");
    }
}

#[cfg(test)]
#[allow(non_snake_case)]
pub fn failWrapper(msg: &str) -> ! {
    panic!("{}", msg);
}

#[cfg(not(test))]
#[allow(non_snake_case)]
pub fn failWrapper(msg: &str) -> ! {
    let msg_bytes = msg.as_bytes();
    unsafe { fail(msg_bytes.as_ptr(), msg_bytes.len()); }
}

pub fn keccak_hash_helper(value: &[u8], result: &mut [u8; 32]) {
    unsafe { keccakHash(value.as_ptr(), value.len(), result.as_mut_ptr()); }
}

pub fn keccak_hash(value: &Bytes) -> [u8; 32] {
    let mut fingerprint = [0_u8; 32];
    keccak_hash_helper(value.chunk(), &mut fingerprint);
    fingerprint
}


pub fn keccak_hash_int(value: &Bytes) -> U256 {
    let fingerprint = keccak_hash(value);
    U256::from_array_le(fingerprint)
}