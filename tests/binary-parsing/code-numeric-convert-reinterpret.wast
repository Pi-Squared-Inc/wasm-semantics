(module $mymodule
  (func (param i32) (result i32)

    i32.const 0
    f32.convert_i32_s
    i32.reinterpret_f32
    drop

    i32.const 0
    f64.convert_i32_s
    i64.reinterpret_f64
    drop

    i32.const 0
    f32.reinterpret_i32
    drop

    i64.const 0
    f64.reinterpret_i64
    drop

    (return (i32.const 1))
  )
)
