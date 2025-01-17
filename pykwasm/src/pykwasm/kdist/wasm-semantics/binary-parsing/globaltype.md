Parsing [global types](https://webassembly.github.io/spec/core/binary/types.html#global-types)

```k
module BINARY-PARSER-GLOBALTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax GlobalTypeResult ::= globalTypeResult(GlobalType, BytesWithIndex) | ParseError
  syntax GlobalTypeResult ::= parseGlobalType(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-GLOBALTYPE  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-GLOBALTYPE-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax GlobalTypeResult ::= #parseGlobalType1(ValTypeResult)  [function, total]
                            | #parseGlobalType2(ValType, MutResult)  [function, total]

  rule parseGlobalType(BWI:BytesWithIndex) => #parseGlobalType1(parseValType(BWI))
  rule #parseGlobalType1(valTypeResult(T:ValType, BWI:BytesWithIndex))
      => #parseGlobalType2(T, parseMut(BWI))
  rule #parseGlobalType1(E:ParseError) => E
  rule #parseGlobalType2(T:ValType, mutResult(Mut:Mut, BWI:BytesWithIndex))
      => globalTypeResult(Mut T, BWI)
  rule #parseGlobalType2(_, E:ParseError) => E


  syntax MutResult ::= mutResult(Mut, BytesWithIndex) | ParseError
  syntax MutResult ::= parseMut(BytesWithIndex)  [function, total]
                      | #parseMut1(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                      | #parseMut2(BytesWithIndexOrError)  [function, total]
  rule parseMut(BWI:BytesWithIndex) => #parseMut1(BWI, parseConstant(BWI, GLOBAL_CNST))
  rule #parseMut1(_:BytesWithIndex, BWI:BytesWithIndex) => mutResult(const, BWI)
  rule #parseMut1(BWI, _:ParseError) => #parseMut2(parseConstant(BWI, GLOBAL_VAR))
  rule #parseMut2(BWI:BytesWithIndex) => mutResult(var, BWI)
  rule #parseMut2(E:ParseError) => E

endmodule
```
