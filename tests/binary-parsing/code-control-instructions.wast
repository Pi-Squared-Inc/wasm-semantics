(module $mymodule
  (func (param i32) (result i32)
    nop
    (block
      (br 0)
      (br_if 0)
    )
    (call 1 (i32.const 1))
    (return (i32.const 1))
  )
  (func (param i32) (result i32)
    ( unreachable
    )
  )
)
