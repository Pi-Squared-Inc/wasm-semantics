(module $mymodule
  (export "mytable" (table 0))
  (export "mymem" (memory 0))
  (export "myglobal" (global 1))
  (export "myfunc" (func 2))

  (global i32 (i32.const 1))
  (global (mut i64) (i64.const 2))
  (memory 17 20)
  (func (param i32) (result i32)
    (return
      (i32.const 1)
    )
  )
  (func (param i32) (result i32)
    (return
      (i32.const 1)
    )
  )
  (func (param i32) (result i32)
    (return
      (i32.const 1)
    )
  )
  (table 1 funcref)
)
