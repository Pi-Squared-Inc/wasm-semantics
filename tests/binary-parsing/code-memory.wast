(module $mymodule
  (func (param i32) (result i32)
    i32.const 0
    i32.load
    drop

    i32.const 0
    i32.load offset=8
    drop

    i32.const 0
    i32.load align=4
    drop

    i32.const 0
    i32.load offset=8 align=4
    drop

    i32.const 0
    i64.load offset=8
    drop

    i32.const 0
    f32.load offset=8
    drop

    i32.const 0
    f64.load offset=8
    drop

    i32.const 0
    i32.load8_s offset=8
    drop

    i32.const 0
    i32.load8_u offset=8
    drop

    i32.const 0
    i32.load16_s offset=8
    drop

    i32.const 0
    i32.load16_u offset=8
    drop

    i32.const 0
    i64.load8_s offset=8
    drop

    i32.const 0
    i64.load8_u offset=8
    drop

    i32.const 0
    i64.load16_s offset=8
    drop

    i32.const 0
    i64.load16_u offset=8
    drop

    i32.const 0
    i64.load32_s offset=8
    drop

    i32.const 0
    i64.load32_u offset=8
    drop

    i32.const 0
    i32.const 0
    i32.store offset=8

    i32.const 0
    i32.const 0
    i32.store8 offset=8

    i32.const 0
    i32.const 0
    i32.store16 offset=8

    i32.const 0
    i64.const 0
    i64.store offset=8

    i32.const 0
    i64.const 0
    i64.store8 offset=8

    i32.const 0
    i64.const 0
    i64.store16 offset=8

    i32.const 0
    i64.const 0
    i64.store32 offset=8

    i32.const 0
    i32.const 0
    f32.load offset=8
    f32.store offset=8

    i32.const 0
    i32.const 0
    f64.load offset=8
    f64.store offset=8

    memory.size
    drop

    i32.const 0
    memory.grow
    drop

    i32.const 0
    i32.const 0
    i32.const 0
    memory.fill

    i32.const 0
    i32.const 0
    i32.const 0
    memory.copy

    i32.const 0
    i32.const 0
    i32.const 0
    memory.init 0

    data.drop 0
    (return (i32.const 1))
  )
  (memory (;0;) 17)
  (global $g (mut i32) (i32.const 1048576))
  (data (i32.const 1048576) ";askdfja;skdjf")
)
