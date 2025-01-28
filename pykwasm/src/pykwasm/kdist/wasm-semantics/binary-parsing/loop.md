Parsing [loops](https://webassembly.github.io/spec/core/binary/instructions.html#control-instructions),
i.e., a blocktype + instr list.

```k

module BINARY-PARSER-LOOP-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-BLOCK-SYNTAX

  syntax BinaryInstr ::= loop(Block)

endmodule

module BINARY-PARSER-LOOP  [private]
  imports BINARY-PARSER-LOOP-SYNTAX

endmodule
```
