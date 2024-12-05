// SingleChunkStorage is a class which makes it easy to work with storage
// for objects that fit in 32 bytes. Accessing storage will crash (fail) if
// the stored bytes cannot be converted to the value type.
//
// Let's say you want to access a storage object under the name N, with
// key (K1, K2, ..., Kn) and with type T. You need the following:
// * K1 ..., Kn must implement Encodable
// * T must implement TryFrom<U256> and Into<U256>
//
// Then you can build the storage object like this:
// 
// let mut builder = SingleChunkStorageBuilder::<MyValueType>::new(&("Storage name".to_string()))
// builder.add_arg(K1);
// builder.add_arg(K2);
// ...
// builder.add_arg(Kn);
// let storage = builder.build();
//
// In order to set the storage value, do this:
//
// storage.set(&my_value);
//
// In order to get the stored value, do this:
//
// let my_value = storage.get();

use core::marker::PhantomData;
use std::convert::TryFrom;
use std::convert::Into;

use crate::assertions::fail;
use crate::encoder::Encodable;
use crate::encoder::Encoder;
use crate::unsigned::U256;
use crate::ulm;
use crate::ulm_hooks;

pub struct SingleChunkStorage<ValueType:Into<U256> + TryFrom<U256> + 'static> {
    phantom: PhantomData<ValueType>,
    fingerprint: U256,
}

impl<ValueType:Into<U256> + TryFrom<U256, Error = &'static str>> SingleChunkStorage<ValueType> {
    pub fn new(fingerprint: U256) -> Self {
        SingleChunkStorage::<ValueType> { phantom: PhantomData, fingerprint }
    }

    pub fn set(&self, value: ValueType) {
        let converted: U256 = value.into();
        ulm::set_account_storage(&self.fingerprint, &converted);
    }

    pub fn get(&self) -> ValueType {
        let u256 = ulm::get_account_storage(&self.fingerprint);
        match u256.try_into() {
            Ok(v) => v,
            Err(reason) => fail(reason), 
        }
    }
}

pub struct SingleChunkStorageBuilder<ValueType:Into<U256> + TryFrom<U256> + 'static> {
    phantom: PhantomData<ValueType>,
    encoder: Encoder,
}

impl<ValueType:Into<U256> + TryFrom<U256, Error = &'static str>> SingleChunkStorageBuilder<ValueType> {
    pub fn new(name: &String) -> Self {
        let mut encoder = Encoder::new();
        encoder.add(name);
        Self::from_encoder(encoder)
    }

    fn from_encoder(encoder: Encoder) -> Self {
        SingleChunkStorageBuilder::<ValueType> {
            phantom: PhantomData,
            encoder
        }
    }

    pub fn add_arg(&mut self, arg: &dyn Encodable) {
        self.encoder.add(arg);
    }

    pub fn build(&self) -> SingleChunkStorage<ValueType> {
        let bytes = self.encoder.encode();
        let fingerprint = ulm_hooks::keccak_hash_int(&bytes);
        SingleChunkStorage::new(fingerprint)
    }
}
