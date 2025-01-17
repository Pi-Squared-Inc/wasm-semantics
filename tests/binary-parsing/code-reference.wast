(module $mymodule
  (func $f (param i32) (result i32)
    (return
      (i32.const 0)
    )
  )
  (func (param i32) (result i32)
    (ref.null func)
    (ref.is_null)
    (return
      (i32.const 1)
    )
  )
)
