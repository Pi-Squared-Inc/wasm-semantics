(module $mymodule
  (elem declare func $f)
  (func $f (param i32) (result i32)
    (return
      (i32.const 0)
    )
  )
  (func (param i32) (result i32)
    (ref.func 0)
    (return
      (i32.const 1)
    )
  )
)
