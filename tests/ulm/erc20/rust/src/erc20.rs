use std::cell::RefCell;
use std::rc::Rc;

use crate::address::Address;
use crate::balance::Balance;
use crate::encoder::Encoder;
use crate::storage::{SingleChunkStorage, SingleChunkStorageBuilder};
use crate::ulm::{log3, Ulm};

fn s_total_supply<'a>(api: Rc<RefCell<dyn Ulm>>) -> SingleChunkStorage<'a, Balance> {
    SingleChunkStorageBuilder::new(api, &("total_supply".to_string())).build()
}

fn s_balances<'a>(api: Rc<RefCell<dyn Ulm>>, address: &Address) -> SingleChunkStorage<'a, Balance> {
    let mut builder = SingleChunkStorageBuilder::new(api, &("balances".to_string()));
    builder.add_arg(address);
    builder.build()
}

fn s_allowances<'a>(api: Rc<RefCell<dyn Ulm>>, account: &Address, spender: &Address) -> SingleChunkStorage<'a, Balance> {
    let mut builder = SingleChunkStorageBuilder::new(api, &("allowances".to_string()));
    builder.add_arg(account);
    builder.add_arg(spender);
    builder.build()
}

// ---------------------------

fn transfer_event(api: &dyn Ulm, from: Address, to: Address, value: &Balance) {
    let mut encoder = Encoder::new();
    encoder.add(value);
    log3(
        api,
        "Transfer(address,address,u256)",
        &from.into(), &to.into(),
        encoder.encode()
    )
}

fn approval_event(api: &dyn Ulm, owner: Address, spender: Address, value: &Balance) {
    let mut encoder = Encoder::new();
    encoder.add(value);
    log3(
        api,
        "Approval(address,address,u256)",
        &owner.into(), &spender.into(),
        encoder.encode()
    )
}
