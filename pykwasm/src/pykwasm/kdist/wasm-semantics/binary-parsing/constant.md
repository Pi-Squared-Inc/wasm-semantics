  Skipping over a constant prefix in the input.

```k
module BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax BytesWithIndexOrError ::= parseConstant(BytesWithIndexOrError, Bytes)  [function, total]
endmodule

module BINARY-PARSER-CONSTANT  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BOOL
  imports K-EQUAL

  rule parseConstant(bwi(Buffer:Bytes, Index:Int), Constant:Bytes)
      => bwi(Buffer, Index +Int lengthBytes(Constant))
      requires Index +Int lengthBytes(Constant) <=Int lengthBytes(Buffer)
          andBool substrBytes(Buffer, Index, Index +Int lengthBytes(Constant)) ==K Constant
  rule parseConstant(bwi(Buffer:Bytes, Index:Int), Constant:Bytes)
      => parseError("parseConstant", ListItem(lengthBytes(Buffer)) ListItem(Index) ListItem(Constant) ListItem(Buffer))
      [owise]
  rule parseConstant(E:ParseError, _:Bytes) => E

endmodule
```
