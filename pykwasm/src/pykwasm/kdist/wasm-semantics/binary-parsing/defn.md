```k
module BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax DefnResult ::= defnResult(Defn, BytesWithIndex) | ParseError
endmodule
```
