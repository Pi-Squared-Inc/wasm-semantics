Parsing an [expr](https://webassembly.github.io/spec/core/binary/instructions.html#binary-expr).

```k
module BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX

  syntax ExprResult ::= exprResult(BinaryInstrs, BytesWithIndex) | ParseError
  syntax ExprResult ::= parseExpr(BytesWithIndex) [function, total]

endmodule

module BINARY-PARSER-EXPR  [private]
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BOOL

  syntax ExprResult ::= #parseExpr(InstrListResult) [function, total]
  rule parseExpr(BWI:BytesWithIndex) => #parseExpr(parseInstrList(BWI))
  rule #parseExpr(instrListResult(Is:BinaryInstrs, false, BWI:BytesWithIndex))
      => exprResult(Is, BWI)
  rule #parseExpr(instrListResult(Is:BinaryInstrs, true, BWI:BytesWithIndex))
      => parseError("#parseExpr", ListItem(Is) ListItem(BWI))
  rule #parseExpr(E:ParseError) => E

endmodule
```
