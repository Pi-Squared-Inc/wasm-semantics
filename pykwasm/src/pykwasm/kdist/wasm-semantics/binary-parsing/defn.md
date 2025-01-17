```k
module BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax BinaryDefn ::= Defn
  syntax DefnResult ::= defnResult(BinaryDefn, BytesWithIndex) | ParseError

endmodule
```
