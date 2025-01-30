Parsing [if](https://webassembly.github.io/spec/core/binary/instructions.html#control-instructions)
instructions.

```k

module BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-BLOCK-SYNTAX

  syntax BinaryInstr ::= if(Block, BinaryInstrs)

  syntax InstrResult ::= parseIf(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-IF  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-TAGS

  syntax InstrResult  ::= #parseIf1(BlockResult)  [function, total]
                        | #parseIfElse1(Block, ExprResult)  [function, total]
  rule parseIf(BWI:BytesWithIndex) => #parseIf1(parseBlock(BWI))
  rule #parseIf1(blockResult(B:Block, true, BWI:BytesWithIndex))
      => #parseIfElse1(B, parseExpr(BWI))
  rule #parseIf1(blockResult(B:Block, false, BWI:BytesWithIndex))
      => instrResult(if(B, .BinaryInstrs), BWI)
  rule #parseIf1(E:ParseError) => E

  rule #parseIfElse1(Then:Block, exprResult(Else:BinaryInstrs, BWI:BytesWithIndex))
      => instrResult(if(Then, Else), BWI)
  rule #parseIfElse1(_:Block, E:ParseError) => E

endmodule
```
