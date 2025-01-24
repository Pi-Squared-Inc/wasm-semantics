// Parsing an [memory section entry](https://webassembly.github.io/spec/core/binary/modules.html#binary-memsec).

```k
module BINARY-PARSER-MEMORY-SYNTAX

  syntax DefnKind ::= "defnMemory"

endmodule

module BINARY-PARSER-MEMORY  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-MEMORY-SYNTAX
  imports WASM

  rule parseDefn(defnMemory, BWI:BytesWithIndex) => parseDefnMemory(BWI)

  syntax DefnResult ::= parseDefnMemory(BytesWithIndex)  [function, total]
                      | #parseDefnMemory1(LimitsResult)  [function, total]
  rule parseDefnMemory(BWI:BytesWithIndex) => #parseDefnMemory1(parseLimits(BWI))
  rule #parseDefnMemory1(limitsResult(L:Limits, BWI:BytesWithIndex))
       => defnResult(#memory(L, ), BWI)
  rule #parseDefnMemory1(E:ParseError) => E

endmodule
```
