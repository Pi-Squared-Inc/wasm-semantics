(module $mymodule
  (func (param i32) (result i32)

    i64.const 0
    i32.wrap_i64
    drop

    i32.const 0
    f32.convert_i32_s
    i32.trunc_f32_s
    drop

    i32.const 0
    f32.convert_i32_s
    i32.trunc_f32_u
    drop

    i32.const 0
    f64.convert_i32_s
    drop

    i32.const 0
    f64.convert_i32_s
    i32.trunc_f64_s
    drop

    i32.const 0
    f64.convert_i32_s
    i32.trunc_f64_u
    drop

    i32.const 0
    i64.extend_i32_s
    drop

    i32.const 0
    i64.extend_i32_u
    drop

    i32.const 0
    f32.convert_i32_s
    i64.trunc_f32_s
    drop

    i32.const 0
    f32.convert_i32_s
    i64.trunc_f32_u
    drop

    i32.const 0
    f64.convert_i32_s
    i64.trunc_f64_s
    drop

    i32.const 0
    f64.convert_i32_s
    i64.trunc_f64_u
    drop

    i32.const 0
    f32.convert_i32_s
    drop

    i32.const 0
    f32.convert_i32_u
    drop

    i64.const 0
    f32.convert_i64_s
    drop

    i64.const 0
    f32.convert_i64_u
    drop

    i32.const 0
    f64.convert_i32_s
    f32.demote_f64
    drop

    i32.const 0
    f64.convert_i32_s
    drop

    i32.const 0
    f64.convert_i32_u
    drop

    i64.const 0
    f64.convert_i64_s
    drop

    i64.const 0
    f64.convert_i64_u
    drop

    i32.const 0
    f32.convert_i32_s
    f64.promote_f32
    drop

    i32.const 0
    i32.extend8_s
    drop

    i32.const 0
    i32.extend16_s
    drop

    i64.const 0
    i64.extend8_s
    drop

    i64.const 0
    i64.extend16_s
    drop

    i64.const 0
    i64.extend32_s
    drop

    (return (i32.const 1))
  )
)
