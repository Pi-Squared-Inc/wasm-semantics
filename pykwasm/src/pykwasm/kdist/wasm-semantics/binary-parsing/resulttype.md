Parsing a [result type](https://webassembly.github.io/spec/core/binary/types.html#binary-resulttype).

```k
module BINARY-PARSER-RESULTTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON

  syntax ResultTypeResult ::= resultTypeResult(VecType, BytesWithIndex) | ParseError
  syntax ResultTypeResult ::= parseResultType(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-RESULTTYPE  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-RESULTTYPE-SYNTAX
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax ResultTypeResult ::= #parseResultType(IntResult)  [function, total]
                            | #parseResultType1(ValTypesResult)  [function, total]

  rule parseResultType(BWI:BytesWithIndex) => #parseResultType(parseLeb128UInt(BWI))
  rule #parseResultType(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseResultType1(parseValTypes(Count, .ValTypes, BWI))
  rule #parseResultType(E:ParseError) => E
  rule #parseResultType1(valTypesResult(V:ValTypes, BWI:BytesWithIndex))
      => resultTypeResult([V], BWI)
  rule #parseResultType1(E:ParseError) => E
endmodule
```
