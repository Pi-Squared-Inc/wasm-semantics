// Parsing a [code object](https://webassembly.github.io/spec/core/binary/modules.html#code-section).

```k
module BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports WASM

  syntax DefnKind ::= "defnCode"

  syntax BinaryDefn ::= BinaryDefnFunctionBody
  syntax BinaryDefnFunctionBody ::= binaryDefnFunctionBody(VecType, BinaryInstrs)

  syntax BinaryDefnFunctionBodies ::= List{BinaryDefnFunctionBody, ""}

endmodule

module BINARY-PARSER-CODE  [private]
  imports BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-LOCALS-SYNTAX
  imports BINARY-PARSER-VALTYPE-SYNTAX
  imports BOOL

  rule parseDefn(defnCode, BWI:BytesWithIndex) => parseDefnCode(BWI)

  syntax DefnResult ::= parseDefnCode(BytesWithIndex)  [function, total]
                      | #parseDefnCode(sizeInBytes:IntResult)  [function, total]
                      | #parseDefnCode1(sizeInBytes:Int, LocalsVecResult)  [function, total]
                      | #parseDefnCode2(sizeInBytes:Int, ValTypes, InstrListResult)  [function, total]
  rule parseDefnCode(BWI:BytesWithIndex) => #parseDefnCode(parseLeb128UInt(BWI))
  rule #parseDefnCode(intResult(Size:Int, BWI:BytesWithIndex))
      => #parseDefnCode1(Size, parseLocalsVec(BWI))
  rule #parseDefnCode(E:ParseError) => E
  rule #parseDefnCode1(Size:Int, localsVecResult(Locals:LocalsVec, BWI:BytesWithIndex))
      => #parseDefnCode2(Size, localsVecToValTypes(Locals), parseInstrList(BWI))
  rule #parseDefnCode1(_, E:ParseError) => E
  rule #parseDefnCode2(_Size:Int, Locals:ValTypes, instrListResult(Is:BinaryInstrs, false, BWI:BytesWithIndex))
      => defnResult(binaryDefnFunctionBody([ Locals ], Is), BWI)
  rule #parseDefnCode2(_Size:Int, Locals:ValTypes, instrListResult(Is:BinaryInstrs, true, BWI:BytesWithIndex))
      => parseError("#parseDefnCode2", ListItem(Locals) ListItem(Is) ListItem(BWI))
  rule #parseDefnCode2(_, _, E:ParseError) => E

endmodule
```
