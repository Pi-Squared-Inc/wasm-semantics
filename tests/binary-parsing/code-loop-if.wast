(module $mymodule
  (func (param i32) (result i32)
    (if
      (br_if 0 (i32.const 1) (local.get 0))
      (then nop)
    )
    (if (result i32)
      (br_if 0 (i32.const 1) (local.get 0))
      (then (i32.const 2))
      (else (i32.const 3))
    )
    (return
      (i32.const 1)
    )
  )
)
