use std::cell::RefCell;
use std::rc::Rc;

use crate::address::Address;
use crate::balance::Balance;
use crate::storage::{SingleChunkStorage, SingleChunkStorageBuilder};
use crate::ulm::Ulm;

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
