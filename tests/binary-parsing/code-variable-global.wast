(module $mymodule
  (func (param i32) (result i32)
    (local i32 i64)
    global.get 0
    global.set 0
    (return (i32.const 1))
  )
  (global $g (mut i32) (i32.const 1048576))
)
