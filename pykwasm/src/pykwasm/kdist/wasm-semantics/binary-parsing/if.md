Parsing [loops](https://webassembly.github.io/spec/core/binary/instructions.html#control-instructions),
i.e., a blocktype + instr list.

```k

module BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-BLOCK-SYNTAX

  syntax BinaryInstr ::= if(Block, BinaryInstrs)

  syntax InstrResult ::= parseIf(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-IF  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BOOL

  syntax InstrResult  ::= #parseIf1(BlockResult)  [function, total]
                        | #parseIfElse1(Block, InstrListResult)  [function, total]
  rule parseIf(BWI:BytesWithIndex) => #parseIf1(parseBlock(BWI))
  rule #parseIf1(blockResult(B:Block, true, BWI:BytesWithIndex))
      => #parseIfElse1(B, parseInstrList(BWI))
  rule #parseIf1(blockResult(B:Block, false, BWI:BytesWithIndex))
      => instrResult(if(B, .BinaryInstrs), BWI)
  rule #parseIf1(E:ParseError) => E

  rule #parseIfElse1(Then:Block, instrListResult(Else:BinaryInstrs, false, BWI:BytesWithIndex))
      => instrResult(if(Then, Else), BWI)
  rule #parseIfElse1(Then:Block, instrListResult(Else:BinaryInstrs, true, BWI:BytesWithIndex))
      => parseError("#parseIfElse1", ListItem(Then) ListItem(Else) ListItem(BWI))
  rule #parseIfElse1(_:Block, E:ParseError) => E

endmodule
```
