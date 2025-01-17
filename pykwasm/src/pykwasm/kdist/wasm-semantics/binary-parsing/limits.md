Parsing [limits](https://webassembly.github.io/spec/core/binary/types.html#limits).

```k

module BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON

  syntax LimitsResult ::= limitsResult(Limits, BytesWithIndex) | ParseError
  syntax LimitsResult ::= parseLimits(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-LIMITS  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-TAGS

  syntax LimitsResult ::= #parseLimits1(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                        | #parseLimits2(BytesWithIndexOrError)  [function, total]
                        | parseLimitsMin(IntResult)  [function, total]
                        | parseLimitsMinMax(IntResult)  [function, total]
                        | #parseLimitsMinMax(Int, IntResult)  [function, total]

  rule parseLimits(BWI:BytesWithIndex) => #parseLimits1(BWI, parseConstant(BWI, LIMITS_MIN))
  rule #parseLimits1(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseLimitsMin(parseLeb128UInt(BWI))
  rule #parseLimits1(BWI:BytesWithIndex, _:ParseError)
      => #parseLimits2(parseConstant(BWI, LIMITS))
  rule #parseLimits2(BWI:BytesWithIndex)
      => parseLimitsMinMax(parseLeb128UInt(BWI))
  rule #parseLimits2(E:ParseError) => E

  rule parseLimitsMin(intResult(Min:Int, BWI:BytesWithIndex))
      => limitsResult(#limitsMin(Min), BWI)
  rule parseLimitsMin(E:ParseError) => E

  rule parseLimitsMinMax(intResult(Min:Int, BWI:BytesWithIndex))
      => #parseLimitsMinMax(Min, parseLeb128UInt(BWI))
  rule parseLimitsMinMax(E:ParseError) => E
  rule #parseLimitsMinMax(Min:Int, intResult(Max:Int, BWI:BytesWithIndex))
      => limitsResult(#limits(Min, Max), BWI)
  rule #parseLimitsMinMax(_, E:ParseError) => E

endmodule
```
