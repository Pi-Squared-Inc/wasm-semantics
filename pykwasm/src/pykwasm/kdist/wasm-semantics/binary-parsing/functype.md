Parsing a [function type](https://webassembly.github.io/spec/core/binary/types.html#binary-functype).

```k
module BINARY-PARSER-FUNCTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports WASM-DATA-COMMON

  syntax DefnResult ::= parseDefnType(BytesWithIndex)  [function, total]

  syntax FuncTypeResult ::= funcTypeResult(FuncType, BytesWithIndex) | ParseError
  syntax FuncTypeResult ::= parseFuncType(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-FUNCTYPE  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-FUNCTYPE-SYNTAX
  imports BINARY-PARSER-RESULTTYPE-SYNTAX
  imports BINARY-PARSER-TAGS
  imports WASM

  syntax DefnResult ::= #parseDefnType(FuncTypeResult)  [function, total]

  rule parseDefnType(BWI:BytesWithIndex) => #parseDefnType(parseFuncType(BWI))

  rule #parseDefnType(funcTypeResult(F:FuncType, BWI:BytesWithIndex))
      => defnResult(#type(F, ), BWI)

  syntax FuncTypeResult ::= #parseFuncType(BytesWithIndexOrError)  [function, total]
                          | #parseFuncType1(ResultTypeResult)  [function, total]
                          | #parseFuncType2(VecType, ResultTypeResult)  [function, total]

  rule parseFuncType(BWI:BytesWithIndex) => #parseFuncType(parseConstant(BWI, TYPE_FUN))
  rule #parseFuncType(BWI:BytesWithIndex) => #parseFuncType1(parseResultType(BWI))
  rule #parseFuncType(E:ParseError) => E
  rule #parseFuncType1(resultTypeResult(V:VecType, BWI:BytesWithIndex))
      => #parseFuncType2(V, parseResultType(BWI))
  rule #parseFuncType1(E:ParseError) => E
  rule #parseFuncType2(V1:VecType, resultTypeResult(V2:VecType, BWI:BytesWithIndex))
      => funcTypeResult(V1 -> V2, BWI:BytesWithIndex)
  rule #parseFuncType2(_:VecType, E:ParseError) => E

endmodule
```