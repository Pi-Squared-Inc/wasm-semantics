Parsing [blocks](https://webassembly.github.io/spec/core/binary/instructions.html#control-instructions),
i.e., a blocktype + instr list.

```k

module BINARY-PARSER-BLOCK-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX
  imports WASM-DATA-COMMON

  syntax Block ::= block(VecType, Instrs)
  syntax BlockResult ::= blockResult(Block, BytesWithIndex) | ParseError

  syntax BlockResult  ::= parseBlock(BytesWithIndex) [function, total]
endmodule

module BINARY-PARSER-BLOCK  [private]
  imports BINARY-PARSER-BLOCK-SYNTAX
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax BlockResult  ::= #parseBlock1(BlockTypeResult) [function, total]
                        | #parseBlock2(BlockType, InstrListResult) [function, total]
  rule parseBlock(BWI:BytesWithIndex) => #parseBlock1(parseBlockType(BWI))
  rule #parseBlock1(blockTypeResult(BT:BlockType, BWI:BytesWithIndex))
      => #parseBlock2(BT, parseInstrList(BWI))
  rule #parseBlock1(E:ParseError) => E
  rule #parseBlock2(BT:BlockType, instrListResult(Is:Instrs, BWI:BytesWithIndex))
      => blockResult(block(blockTypeToVecType(BT), Is), BWI)
  rule #parseBlock2(_:BlockType, E:ParseError) => E

  syntax BlockType ::= "epsilon" | ValType | Int
  syntax BlockTypeResult ::= blockTypeResult(BlockType, BytesWithIndex) | ParseError

  syntax BlockTypeResult  ::= parseBlockType(BytesWithIndex)  [function, total]
                            | #parseBlockType1(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseBlockType2(BytesWithIndex, ValTypeResult)  [function, total]
                            | #parseBlockType3(IntResult)  [function, total]
  rule parseBlockType(BWI:BytesWithIndex)
      => #parseBlockType1(BWI, parseConstant(BWI, TYPE_EMPTY))
  rule #parseBlockType1(_:BytesWithIndex, BWI:BytesWithIndex)
      => blockTypeResult(epsilon, BWI:BytesWithIndex)
  rule #parseBlockType1(BWI:BytesWithIndex, _:ParseError)
      => #parseBlockType2(BWI, parseValType(BWI))
  rule #parseBlockType2(_:BytesWithIndex, valTypeResult(VT:ValType, BWI:BytesWithIndex))
      => blockTypeResult(VT, BWI)
  rule #parseBlockType2(BWI:BytesWithIndex, _:ParseError)
      => #parseBlockType3(parseLeb128SInt(BWI))
  rule #parseBlockType3(intResult(Value:Int, BWI:BytesWithIndex))
      => blockTypeResult(Value, BWI)
  rule #parseBlockType3(E:ParseError) => E

  syntax VecType ::= blockTypeToVecType(BlockType)  [function, total]
  rule blockTypeToVecType(epsilon) => [ .ValTypes ]
  rule blockTypeToVecType(ValType) => [ ValType .ValTypes ]
  // TODO: Also lookup the int in the type section.

endmodule
```
