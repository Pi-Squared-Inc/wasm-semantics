use std::cell::RefCell;
use std::rc::Rc;

use crate::storage::{SingleChunkStorage, SingleChunkStorageBuilder};
use crate::ulm::Ulm;
use crate::unsigned::U256;

pub struct Contract {
  api: Rc<RefCell<dyn Ulm>>
}

impl Contract {
    pub fn new(api: Rc<RefCell<dyn Ulm>>) -> Self {
        Contract { api }
    }

    // ---------------------------

    fn s_counter<'a>(&self) -> SingleChunkStorage<'a, U256> {
        SingleChunkStorageBuilder::new(self.api.clone(), &("counter".to_string())).build()
    }

    // ---------------------------

    pub fn init(&self) {
        self.s_counter().set(U256::from_u64(0));
    }

    pub fn inc_counter(&self) -> bool {
        self.s_counter().set(self.s_counter().get() + U256::from_u64(1));
        true
    }

    pub fn get_counter(&self) -> U256 {
        self.s_counter().get()
    }
}
