Parsing a [ref type](https://webassembly.github.io/spec/core/binary/types.html#binary-reftype).

```k
module BINARY-PARSER-REFTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON-SYNTAX

  syntax RefTypeResult ::= refTypeResult(RefValType, BytesWithIndex) | ParseError
  syntax RefTypeResult ::= parseRefType(BytesWithIndex) [function, total]

endmodule

module BINARY-PARSER-REFTYPE  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-REFTYPE-SYNTAX
  imports BINARY-PARSER-TAGS

  syntax RefTypeResult  ::= #parseFuncRef(BytesWithIndex, BytesWithIndexOrError) [function, total]
                          | #parseExtRef(BytesWithIndex, BytesWithIndexOrError) [function, total]
  rule parseRefType(BWI:BytesWithIndex)
      => #parseFuncRef(BWI, parseConstant(BWI, TYPE_FUN_REF))
  rule #parseFuncRef(_, BWI:BytesWithIndex) => refTypeResult(funcref, BWI)
  rule #parseFuncRef(BWI:BytesWithIndex, _:ParseError)
      => #parseExtRef(BWI, parseConstant(BWI, TYPE_EXT_REF))
  rule #parseExtRef(_, BWI:BytesWithIndex) => refTypeResult(externref, BWI)
  rule #parseExtRef(_:BytesWithIndex, E:ParseError)
      => E

endmodule
```
