Parses a [memarg](https://webassembly.github.io/spec/core/binary/instructions.html#binary-memarg)

```k
module BINARY-PARSER-MEMARG-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax MemArg ::= memArg(align:Int, offset:Int)
  syntax MemArgResult ::= memArgResult(MemArg, BytesWithIndex) | ParseError
  syntax MemArgResult ::= parseMemArg(BytesWithIndex) [function, total]

  syntax Int ::= getMemArgOffset(MemArg)  [function, total]
endmodule

module BINARY-PARSER-MEMARG  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-MEMARG-SYNTAX

  syntax MemArgResult ::= #parseMemArg1(IntResult) [function, total]
                        | #parseMemArg2(Int, IntResult) [function, total]
  rule parseMemArg(BWI:BytesWithIndex) => #parseMemArg1(parseLeb128UInt(BWI))
  rule #parseMemArg1(intResult(Value:Int, BWI:BytesWithIndex))
      => #parseMemArg2(Value, parseLeb128UInt(BWI))
  rule #parseMemArg1(E:ParseError) => E
  rule #parseMemArg2(Align:Int, intResult(Offset:Int, BWI:BytesWithIndex))
      => memArgResult(memArg(Align, Offset), BWI)
  rule #parseMemArg2(_:Int , E:ParseError) => E

  rule getMemArgOffset(memArg(_, Offset:Int)) => Offset
endmodule
```
