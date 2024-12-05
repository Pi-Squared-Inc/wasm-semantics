use crate::unsigned::U256;

extern "C" {
    // key and value must have a length of exactly 32.
    #[allow(non_snake_case)]
    pub fn GetAccountStorage(key: *const u8, value: *mut u8);

    // key and value must have a length of exactly 32.
    #[allow(non_snake_case)]
    pub fn SetAccountStorage(key: *const u8, value: *const u8);
}

pub fn get_account_storage_helper(key: &[u8; 32], value: &mut [u8; 32]) {
    unsafe { GetAccountStorage(key.as_ptr(), value.as_mut_ptr()); }
}
pub fn get_account_storage(key: &U256) -> U256 {
    let mut key_bytes = [0_u8; 32];
    key.copy_to_array_le(&mut key_bytes);

    let mut value_bytes = [0_u8; 32];
    get_account_storage_helper(&key_bytes, &mut value_bytes);

    U256::from_array_le(value_bytes)
}

pub fn set_account_storage_helper(key: &[u8; 32], value: &[u8; 32]) {
    unsafe { SetAccountStorage(key.as_ptr(), value.as_ptr()); }
}
pub fn set_account_storage(key: &U256, value: &U256) {
    let mut key_bytes = [0_u8; 32];
    key.copy_to_array_le(&mut key_bytes);

    let mut value_bytes = [0_u8; 32];
    value.copy_to_array_le(&mut value_bytes);

    set_account_storage_helper(&key_bytes, &value_bytes);
}
