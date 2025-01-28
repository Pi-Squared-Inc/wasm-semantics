(module $mymodule
  (func (param i32) (result i32)
    (local i32 i64)
    local.get 0
    local.set 0
    local.get 1
    local.set 1
    local.get 0
    local.tee 0
    drop
    (return (i32.const 1))
  )
)
