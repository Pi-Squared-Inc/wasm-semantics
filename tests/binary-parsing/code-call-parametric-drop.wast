(module $mymodule
  (func (param i32) (result i32)
    (i32.const 1)
    drop
    (i32.const 7)
    (i32.const 5)
    (i32.const 1)
    select
    (return (i32.const 1))
  )
)
