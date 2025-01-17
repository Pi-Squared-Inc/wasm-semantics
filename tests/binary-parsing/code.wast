(module $mymodule
  (func (param i32) (result i32)
    (local)
    (return
      (if (result i32)
        (i32.eq (local.get 0) (i32.const 0))
        (i32.const 1)
        (i32.mul (local.get 0) (call 0 (i32.sub (local.get 0) (i32.const 1))))
      )
    )
  )
)
