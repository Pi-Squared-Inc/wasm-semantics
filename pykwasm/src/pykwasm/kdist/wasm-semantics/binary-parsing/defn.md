```k
module BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax BinaryDefn ::= Defn
  syntax DefnResult ::= defnResult(BinaryDefn, BytesWithIndex) | ParseError

  syntax BinaryDefns ::= List{BinaryDefn, ""}

  syntax DefnOrError ::= Defn | ParseError
  syntax DefnsOrError ::= Defns | ParseError

endmodule
```
