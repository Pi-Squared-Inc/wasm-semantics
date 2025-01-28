Random functionality that does not fit elsewhere.

```k
module BINARY-PARSER-HELPERS-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON

  syntax Instr ::= buildCallIndirect(typeIdx:Int, tabeIdx:Int)  [function, total]
  syntax Instr ::= buildBrTable(targets:Ints, defaultTarget:Int)  [function, total]

endmodule

module BINARY-PARSER-HELPERS  [private]
  imports BINARY-PARSER-HELPERS-SYNTAX
  imports WASM

  rule buildCallIndirect(TypeIdx:Int, TableIdx:Int) => #call_indirect(TableIdx, (type TypeIdx))

  rule buildBrTable(Is:Ints, I:Int) => #br_table(#appendInts(Is, I))

endmodule
```
