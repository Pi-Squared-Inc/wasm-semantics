(module $mymodule
  (func (param i32) (result i32)

    i32.const 0
    i32.const 0
    i32.const 0
    memory.init 0

    data.drop 0
    (return (i32.const 1))
  )
  (memory (;0;) 17)
  (data (i32.const 1048576) ";askdfja;skdjf")
)
