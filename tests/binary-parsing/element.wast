(module $mymodule
  (table 1 funcref)

  (elem funcref)
  (elem funcref (ref.func 0))
  (elem funcref (ref.func 0) (ref.func 1))

  (elem (table 0) (offset (i32.const 0)) funcref)
  (elem (table 0) (offset (i32.const 0)) funcref (ref.func 0))
  (elem (table 0) (offset (i32.const 0)) funcref (ref.func 0) (ref.func 1))

  (elem declare funcref)
  (elem declare funcref (ref.func 0))
  (elem declare funcref (ref.func 0) (ref.func 1))

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
)
