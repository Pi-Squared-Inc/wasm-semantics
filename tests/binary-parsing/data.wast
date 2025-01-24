(module $mymodule
  (memory 17)
  (data "data-passive")
  (data (offset (i32.const 1048576)) "data-active")
  (data (memory 0) (offset (i32.const 1048576)) "data-active-idx")
)
