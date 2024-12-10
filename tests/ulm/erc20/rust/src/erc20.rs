use std::cell::RefCell;
use std::rc::Rc;

use crate::address::Address;
use crate::balance::Balance;
use crate::encoder::Encoder;
use crate::storage::{SingleChunkStorage, SingleChunkStorageBuilder};
use crate::ulm::{log3, Ulm};

struct Erc20 {
  api: Rc<RefCell<dyn Ulm>>
}

impl Erc20 {
    pub fn new(api: Rc<RefCell<dyn Ulm>>) -> Self {
        Erc20 { api }
    }

    // ---------------------------

    fn s_total_supply<'a>(&self) -> SingleChunkStorage<'a, Balance> {
        SingleChunkStorageBuilder::new(self.api.clone(), &("total_supply".to_string())).build()
    }

    fn s_balances<'a>(&self, address: &Address) -> SingleChunkStorage<'a, Balance> {
        let mut builder = SingleChunkStorageBuilder::new(self.api.clone(), &("balances".to_string()));
        builder.add_arg(address);
        builder.build()
    }

    fn s_allowances<'a>(&self, account: &Address, spender: &Address) -> SingleChunkStorage<'a, Balance> {
        let mut builder = SingleChunkStorageBuilder::new(self.api.clone(), &("allowances".to_string()));
        builder.add_arg(account);
        builder.add_arg(spender);
        builder.build()
    }

    // ---------------------------

    fn transfer_event(&self, from: Address, to: Address, value: &Balance) {
        let mut encoder = Encoder::new();
        encoder.add(value);
        log3(
            &*self.api.borrow(),
            "Transfer(address,address,u256)",
            &from.into(), &to.into(),
            encoder.encode()
        )
    }

    fn approval_event(&self, owner: Address, spender: Address, value: &Balance) {
        let mut encoder = Encoder::new();
        encoder.add(value);
        log3(
            &*self.api.borrow(),
            "Approval(address,address,u256)",
            &owner.into(), &spender.into(),
            encoder.encode()
        )
    }

}
