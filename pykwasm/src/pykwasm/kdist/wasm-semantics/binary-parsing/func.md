// Parsing a [func type id](https://webassembly.github.io/spec/core/binary/modules.html#function-section).

```k
module BINARY-PARSER-FUNC-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax DefnResult ::= parseDefnFunc(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-FUNC  [private]
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-FUNC-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX

  syntax DefnResult ::= #parseDefnFunc(IntResult)  [function, total]

  rule parseDefnFunc(BWI:BytesWithIndex) => #parseDefnFunc(parseLeb128UInt(BWI))
  rule #parseDefnFunc(intResult(TypeIndex:Int, BWI:BytesWithIndex))
      => defnResult(binaryDefnFunctionType(TypeIndex), BWI)
  rule #parseDefnFunc(E:ParseError) => E

endmodule
```
