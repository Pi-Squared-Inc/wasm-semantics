// Parsing an [expr/instr list](https://webassembly.github.io/spec/core/binary/instructions.html#binary-expr).

```k
module BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-INSTR-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax BinaryInstrs ::= List{BinaryInstr, ""}

  syntax InstrListResult ::= instrListResult(BinaryInstrs, endsWithElse: Bool, BytesWithIndex) | ParseError
  syntax InstrListResult ::= parseInstrList(BytesWithIndex) [function, total]

  syntax InstrsOrError ::= Instrs | ParseError
endmodule

module BINARY-PARSER-INSTR-LIST  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BOOL

  syntax InstrListResult  ::= #parseInstrList1(BytesWithIndex, BinaryInstrs) [function, total]
                            | #parseInstrList2(BytesWithIndex, BytesWithIndexOrError, BinaryInstrs) [function, total]
                            | #parseInstrList3(BytesWithIndex, BytesWithIndexOrError, BinaryInstrs) [function, total]
                            | #parseInstrList4(InstrResult, BinaryInstrs) [function, total]

  rule parseInstrList(BWI:BytesWithIndex) => #parseInstrList1(BWI, .BinaryInstrs)
  rule #parseInstrList1(BWI:BytesWithIndex, Is:BinaryInstrs)
      => #parseInstrList2(BWI, parseConstant(BWI, END), Is)
  rule #parseInstrList2(_:BytesWithIndex, BWI:BytesWithIndex, Is:BinaryInstrs)
      => instrListResult(reverse(Is), false, BWI)
  rule #parseInstrList2(BWI:BytesWithIndex, _:ParseError, Is:BinaryInstrs)
      => #parseInstrList3(BWI, parseConstant(BWI, ELSE), Is)
  rule #parseInstrList3(_:BytesWithIndex, BWI:BytesWithIndex, Is:BinaryInstrs)
      => instrListResult(reverse(Is), true, BWI)
  rule #parseInstrList3(BWI:BytesWithIndex, _:ParseError, Is:BinaryInstrs)
      => #parseInstrList4(parseInstr(BWI), Is)
  rule #parseInstrList4(instrResult(I:BinaryInstr, BWI:BytesWithIndex), Is:BinaryInstrs)
      => #parseInstrList1(BWI, I Is)
  rule #parseInstrList4(E:ParseError, _) => E


  syntax BinaryInstrs ::= reverse(BinaryInstrs)  [function, total]
                  | #reverse(BinaryInstrs, BinaryInstrs)  [function, total]

  rule reverse(I:BinaryInstrs) => #reverse(I, .BinaryInstrs)
  rule #reverse(.BinaryInstrs, Is:BinaryInstrs) => Is
  rule #reverse(I:BinaryInstr I1:BinaryInstrs, I2:BinaryInstrs) => #reverse(I1, I I2)
endmodule
```
