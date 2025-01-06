use bytes::Bytes;
use core::cell::RefCell;
use std::rc::Rc;

use crate::assertions::fail;
use crate::decoder::Decoder;
use crate::encoder::Encoder;
use crate::contract::Contract;
use crate::require;
use crate::ulm;
use crate::unsigned::U256;

fn same_signature(api: &dyn ulm::Ulm, expected: &Bytes, signature: &str) -> bool {
    expected == &Bytes::copy_from_slice(&ulm::endpoint_fingerprint(api, signature))
}

#[cfg(not(test))]
#[no_mangle]
#[allow(non_snake_case)]
pub fn ulmDispatchCaller(init: bool) {
    dispatch(ulm::impl_::UlmImpl::new(), init);
}

fn dispatch(api: Rc<RefCell<dyn ulm::Ulm>>, init: bool) {
    let mut buffer = ulm::call_data(&*api.borrow());
    if init {
        initCaller(api, buffer);
    } else {
        require!(buffer.len() >= 4, "Buffer without function signature");
        let arguments = buffer.split_off(4);
        let signature = buffer;
        if same_signature(&*api.borrow(), &signature, "incCounter()") {
            incCaller(api, arguments);
        } else if same_signature(&*api.borrow(), &signature, "getCounter()") {
            getCaller(api, arguments);
        } else {
            fail("Unknown endpoint");
        }
    }
}

#[allow(non_snake_case)]
fn initCaller(api: Rc<RefCell<dyn ulm::Ulm>>, arguments: Bytes) {
    let decoder: Decoder<()> = Decoder::from_buffer(arguments);
    decoder.check_done();

    let contract = Contract::new(api.clone());
    contract.init();
}

#[allow(non_snake_case)]
fn incCaller(api: Rc<RefCell<dyn ulm::Ulm>>, arguments: Bytes) {
    let decoder: Decoder<()> = Decoder::from_buffer(arguments);
    decoder.check_done();

    let contract = Contract::new(api.clone());
    let result = contract.inc_counter();

    let mut encoder = Encoder::new();
    encoder.add(&U256::from_bool(result));
    ulm::set_output(&mut *api.borrow_mut(), &encoder.encode());
}

#[allow(non_snake_case)]
fn getCaller(api: Rc<RefCell<dyn ulm::Ulm>>, arguments: Bytes) {
    let decoder: Decoder<()> = Decoder::from_buffer(arguments);
    decoder.check_done();

    let contract = Contract::new(api.clone());
    let counter = contract.get_counter();

    let mut encoder = Encoder::new();
    encoder.add(&counter);
    ulm::set_output(&mut *api.borrow_mut(), &encoder.encode());
}
