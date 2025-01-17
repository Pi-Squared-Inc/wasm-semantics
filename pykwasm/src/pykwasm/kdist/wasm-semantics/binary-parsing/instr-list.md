// Parsing an [expr/instr list](https://webassembly.github.io/spec/core/binary/instructions.html#binary-expr).

```k
module BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax InstrListResult ::= instrListResult(Instrs, BytesWithIndex) | ParseError
  syntax InstrListResult ::= parseInstrList(BytesWithIndex) [function, total]

endmodule

module BINARY-PARSER-INSTR-LIST  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-INSTRS-SYNTAX
  imports BINARY-PARSER-TAGS

  syntax InstrListResult  ::= #parseInstrList1(BytesWithIndex, Instrs) [function, total]
                            | #parseInstrList2(BytesWithIndex, BytesWithIndexOrError, Instrs) [function, total]
                            | #parseInstrList3(BytesWithIndex, InstrResult, Instrs) [function, total]

  rule parseInstrList(BWI:BytesWithIndex) => #parseInstrList1(BWI, .Instrs)
  rule #parseInstrList1(BWI:BytesWithIndex, Is:Instrs)
      => #parseInstrList2(BWI, parseConstant(BWI, END), Is)
  rule #parseInstrList2(_:BytesWithIndex, BWI:BytesWithIndex, Is:Instrs)
      => instrListResult(reverse(Is), BWI)
  rule #parseInstrList2(BWI:BytesWithIndex, _:ParseError, Is:Instrs)
      => #parseInstrList3(BWI, parseInstr(BWI), Is)
  rule #parseInstrList3(BWI:BytesWithIndex, instrResult(I:Instr, BWI:BytesWithIndex), Is:Instrs)
      => #parseInstrList1(BWI, I Is)
  rule #parseInstrList3(_, E:ParseError, _) => E


  syntax Instrs ::= reverse(Instrs)  [function, total]
                  | #reverse(Instrs, Instrs)  [function, total]

  rule reverse(I:Instrs) => #reverse(I, .Instrs)
  rule #reverse(.Instrs, Is:Instrs) => Is
  rule #reverse(I:Instr I1:Instrs, I2:Instrs) => #reverse(I1, I I2)
endmodule
```
