(module $mymodule
  (table 2 funcref)
  (table 2 funcref)
  (elem (i32.const 0) 0)
  (elem (i32.const 0) 0)
  (func (param i32) (result i32)
    (i32.const 1)
    (i32.const 1)
    (table.get 0)
    (table.set 0)

    (table.size 0)
    drop

    (i32.const 1)
    (table.get 0)
    (i32.const 10)
    (table.grow 0)
    drop

    (i32.const 10)
    (i32.const 1)
    (table.get 0)
    (i32.const 10)
    (table.fill 0)

    (i32.const 1)
    (i32.const 1)
    (i32.const 1)
    (table.copy 0 1)

    (i32.const 1)
    (i32.const 1)
    (i32.const 1)
    (table.init 0 1)

    (elem.drop 0)
    (return (i32.const 1))
  )
)
