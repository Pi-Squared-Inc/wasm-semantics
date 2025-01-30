```k
module BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax BinaryDefn ::= Defn
  syntax DefnResult ::= defnResult(BinaryDefn, BytesWithIndex) | ParseError
  syntax DefnKind
  syntax DefnResult ::= parseDefn(DefnKind, BytesWithIndex)  [function, total]

  syntax BinaryDefns ::= List{BinaryDefn, ""}

  syntax DefnOrError ::= Defn | ParseError
  syntax DefnsOrError ::= Defns | ParseError

endmodule
```
