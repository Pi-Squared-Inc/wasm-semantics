// Parsing a [global section entry](https://webassembly.github.io/spec/core/binary/modules.html#binary-globalsec).

```k
module BINARY-PARSER-GLOBAL-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports WASM

  syntax DefnKind ::= "defnGlobal"

  syntax BinaryDefnGlobals ::= List{BinaryDefnGlobal, ""}

  syntax BinaryDefnGlobal ::= #binaryGlobal
            ( type: GlobalType
            , instrs: BinaryInstrs
            )
  syntax BinaryDefn ::= BinaryDefnGlobal

endmodule

module BINARY-PARSER-GLOBAL  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-GLOBAL-SYNTAX
  imports BINARY-PARSER-GLOBALTYPE-SYNTAX
  imports WASM

  rule parseDefn(defnGlobal, BWI:BytesWithIndex) => parseDefnGlobal(BWI)

  syntax DefnResult ::= parseDefnGlobal(BytesWithIndex)  [function, total]
                      | #parseDefnGlobal1(GlobalTypeResult)  [function, total]
                      | #parseDefnGlobal2(GlobalType, ExprResult)  [function, total]
  rule parseDefnGlobal(BWI:BytesWithIndex) => #parseDefnGlobal1(parseGlobalType(BWI))
  rule #parseDefnGlobal1(globalTypeResult(T:GlobalType, BWI:BytesWithIndex))
      => #parseDefnGlobal2(T, parseExpr(BWI))
  rule #parseDefnGlobal1(E:ParseError) => E
  rule #parseDefnGlobal2(T:GlobalType, exprResult(I:BinaryInstrs, BWI:BytesWithIndex))
      => defnResult(#binaryGlobal(T, I), BWI)
  rule #parseDefnGlobal2(_:GlobalType, E:ParseError) => E

endmodule
```
