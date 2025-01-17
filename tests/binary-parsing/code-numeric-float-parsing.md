(module $mymodule
  (func (param i32) (result i32)
    f32.const 0.0
    drop

    f64.const 0.0
    drop

    (return (i32.const 1))
  )
  (memory (;0;) 17)
  (global $g (mut i32) (i32.const 1048576))
  (data (i32.const 1048576) ";askdfja;skdjf")
)
