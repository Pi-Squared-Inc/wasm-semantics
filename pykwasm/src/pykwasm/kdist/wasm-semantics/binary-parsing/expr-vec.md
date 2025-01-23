Parsing an expr vec.

```k
module BINARY-PARSER-EXPR-VEC-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX

  syntax ExprVec ::= List{BinaryInstrs, ""}
  syntax ExprVecResult ::= exprVecResult(ExprVec, BytesWithIndex) | ParseError
  syntax ExprVecResult ::= parseExprVec(BytesWithIndex) [function, total]

endmodule

module BINARY-PARSER-EXPR-VEC  [private]
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-EXPR-VEC-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX

  syntax ExprVecResult  ::= #parseExprVec1(IntResult) [function, total]
                          | #parseExprVec2(Int, ExprVec, BytesWithIndex) [function, total]
                          | #parseExprVec3(Int, ExprVec, ExprResult) [function, total]
  rule parseExprVec(BWI:BytesWithIndex) => #parseExprVec1(parseLeb128UInt(BWI))
  rule #parseExprVec1(intResult(I:Int, BWI:BytesWithIndex))
      => #parseExprVec2(I, .ExprVec, BWI)
  rule #parseExprVec1(E:ParseError) => E
  rule #parseExprVec2(0, Is:ExprVec, BWI:BytesWithIndex) => exprVecResult(reverse(Is), BWI)
  rule #parseExprVec2(I:Int, Is:ExprVec, BWI:BytesWithIndex)
      => #parseExprVec3(I -Int 1, Is, parseExpr(BWI))
      requires I >Int 0
  rule #parseExprVec2(I:Int, Is:ExprVec, BWI:BytesWithIndex)
      => parseError("#parseExprVec2", ListItem(I) ListItem(Is) ListItem(BWI))
      requires I <Int 0
  rule #parseExprVec3(I:Int, Is:ExprVec, exprResult(E:BinaryInstrs, BWI:BytesWithIndex))
      => #parseExprVec2(I, E Is, BWI)
  rule #parseExprVec3(_, _, E:ParseError) => E


  syntax ExprVec  ::= reverse(ExprVec)  [function, total]
                    | #reverse(ExprVec, ExprVec)  [function, total]

  rule reverse(Es:ExprVec) => #reverse(Es, .ExprVec)
  rule #reverse(.ExprVec, Es:ExprVec) => Es
  rule #reverse(E:BinaryInstrs Es1:ExprVec, Es2:ExprVec) => #reverse(Es1, E Es2)
endmodule
```
