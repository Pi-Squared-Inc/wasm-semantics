(module $mymodule
  (table 2 funcref)
  (func (param i32) (result i32)
    (call_indirect (result i32) (i32.const 1))
    (return (i32.const 1))
  )
)
