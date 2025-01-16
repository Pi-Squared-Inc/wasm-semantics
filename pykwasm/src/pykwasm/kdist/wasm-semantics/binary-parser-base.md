```k
module BINARY-PARSER-BASE
  imports BYTES
  imports INT
  imports LIST
  imports WASM

  syntax ParseError ::= parseError(String, List)
  syntax BytesWithIndex ::= bwi(Bytes, Int)
  syntax BytesWithIndexOrError ::= BytesWithIndex | ParseError

  ```

  Parsing blocks

  ```k

  syntax Block ::= block(VecType, Instrs)
  syntax BlockResult ::= blockResult(Block, BytesWithIndex) | ParseError

  syntax BlockResult  ::= parseBlock(BytesWithIndex) [function, total]
                        | #parseBlock1(BlockTypeResult) [function, total]
                        | #parseBlock2(BlockType, InstrListResult) [function, total]
  rule parseBlock(BWI:BytesWithIndex) => #parseBlock1(parseBlockType(BWI))
  rule #parseBlock1(BlockTypeResult(BT:BlockType, BWI:BytesWithIndex))
      => #parseBlock2(BT, parseInstrList(BWI))
  rule parseBlock1(E:ParseError) => E
  rule #parseBlock2(BT:BlockType, InstrListResult(Is:Instrs, BWI:BytesWithIndex))
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
  rule #parseBlockType3(IntResult(Value:Int, BWI:BytesWithIndex))
      => blockTypeResult(Value, BWI)
  rule #parseBlockType3(E:ParseError) => E

  syntax VecType ::= blockTypeToVecType(BlockType)  [function, total]
  rule blockTypeToVecType(epsilon) => [ .ValTypes ]
  rule blockTypeToVecType(ValType) => [ ValType : .ValTypes ]
  // TODO: Also lookup the int in the type section.

```

  Parsing InstrListResult is declared here, but it's implemented in a place where
  individual instruction parsing is available.

```k

  syntax InstrListResult ::= instrListResult(Instrs, BytesWithIndex) | ParseError

  syntax InstrListResult  ::= parseInstrList(BytesWithIndex, Instrs) [function, total]

```

  Parsing ValType

```k


  syntax ValTypeResult ::= valTypeResult(ValType, BytesWithIndex) | ParseError
  syntax ValTypeResult  ::= parseValType(BytesWithIndex)  [function, total]
                          | #parseValTypeI32(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeI64(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeF32(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeF64(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeVec(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeFuncRef(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeExtRef(BytesWithIndex, BytesWithIndexOrError)  [function, total]
  rule parseValType(BWI:BytesWithIndex)
      => #parseValTypeI32(BWI, parseConstant(BWI, TYPE_I32))
  rule #parseValTypeI32(_, BWI:BytesWithIndex) => valTypeResult(i32, BWI)
  rule #parseValTypeI32(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeI64(BWI, parseConstant(BWI, TYPE_I64))
  rule #parseValTypeI64(_, BWI:BytesWithIndex) => valTypeResult(i64, BWI)
  rule #parseValTypeI64(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeF32(BWI, parseConstant(BWI, TYPE_F32))
  rule #parseValTypeF32(_, BWI:BytesWithIndex) => valTypeResult(f32, BWI)
  rule #parseValTypeF32(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeF64(BWI, parseConstant(BWI, TYPE_F64))
  rule #parseValTypeF64(_, BWI:BytesWithIndex) => valTypeResult(f64, BWI)
  rule #parseValTypeF64(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeVec(BWI, parseConstant(BWI, TYPE_VEC))
  rule #parseValTypeVec(_:BytesWithIndex, _:BytesWithIndex)
      => parseError("#parseValTypeVec: v128 not implemented", .List)
  rule #parseValTypeVec(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeFuncRef(BWI, parseConstant(BWI, TYPE_FUN_REF))
  rule #parseValTypeFuncRef(_, BWI:BytesWithIndex) => valTypeResult(funcref, BWI)
  rule #parseValTypeFuncRef(BWI:BytesWithIndex, _:ParseError)
      => #parseValTypeExtRef(BWI, parseConstant(BWI, TYPE_EXT_REF))
  rule #parseValTypeExtRef(_, BWI:BytesWithIndex) => valTypeResult(externref, BWI)
  rule #parseValTypeExtRef(_:BytesWithIndex, E:ParseError)
      => E

```

  Parsing MemArg

```k

  syntax MemArg ::= memArg(align:Int, offset:Int)
  syntax MemArgResult ::= memArgResult(MemArg, BytesWithIndex) | ParseError
  syntax MemArgResult ::= parseMemArg(BytesWithIndex) [function, total]
                        | #parseMemArg1(IntResult) [function, total]
                        | #parseMemArg2(Int, IntResult) [function, total]
  rule parseMemArg(BWI:BytesWithIndex) => #parseMemArg1(parseLeb128UInt(BWI))
  rule #parseMemArg1(IntResult(Value:Int, BWI:BytesWithIndex))
      => #parseMemArg2(Value, parseLeb128UInt(BWI))
  rule #parseMemArg1(E:ParseError) => E
  rule #parseMemArg2(Align:Int, IntResult(Offset:Int, BWI:BytesWithIndex))
      => memArgResult(memArg(Align, Offset), BWI)
  rule #parseMemArg2(_:Int , E:ParseError) => E

```

  Parsing floats.

```k

  syntax Float64Result ::= float64Result(Float, BytesWithIndex) | ParseError
  syntax Float64Result  ::= parseFloat64(BytesWithIndex)  [function, total]
                          | #parseFloat64(BytesResult)  [function, total]
  rule parseFloat64(BWI:BytesWithIndex) => #parseFloat64(parseBytes(BWI, 8))
  rule #parseFloat64(BytesResult(Bytes:Bytes, BWI:BytesWithIndex))
      => float64Result(bytesToFloat(Bytes), BWI)
  rule #parseFloat64(E:ParseError) => E

  syntax Float32Result ::= float64Result(Float, BytesWithIndex) | ParseError
  syntax Float32Result  ::= parseFloat32(BytesWithIndex)  [function, total]
                          | #parseFloat32(BytesResult)  [function, total]
  rule parseFloat32(BWI:BytesWithIndex) => #parseFloat32(parseBytes(BWI, 4))
  rule #parseFloat32(BytesResult(Bytes:Bytes, BWI:BytesWithIndex))
      => float32Result(bytesToFloat(Bytes), BWI)
  rule #parseFloat32(E:ParseError) => E

  syntax Float ::= bytesToFloat(Bytes) [function, total]
  // TODO: implement.
```

  Parsing ints.
  See the [LEB128 encoding](https://en.wikipedia.org/wiki/LEB128) for more details.

```k

  syntax IntResult ::= intResult(value:Int, remainder:BytesWithIndex) | ParseError

  syntax Bool ::= bit8IsSet(Int) [function, total]
  rule bit8IsSet(I:Int) => I &Int 128 =/=Int 0

  syntax Int ::= clearBit8(Int) [function, total]
  rule clearBit8(I:Int) => I ^Int (I &Int 128)

  syntax IntList ::= List{Int, ":"}
  syntax IntListResult ::= intListResult(IntList, BytesWithIndex) | ParseError
  syntax IntListResult  ::= parseLeb128IntChunks(BytesWithIndex) [function, total]
                          | #parseLeb128IntChunks(Int, IntListResult) [function, total]

  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => parseError("parseLeb128IntChunks", ListItem(lengthBytes(Buffer)) ListItem(I) ListItem(Buffer))
      requires I <Int 0 orBool lengthBytes(Buffer) <=Int I
  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => #parseLeb128IntChunks(clearBit8(Buffer[I]), parseLeb128IntChunks(bwi(Buffer, I +Int 1)))
      requires 0 <=Int I andBool I <Int lengthBytes(Buffer)
          andBool bit8IsSet(Buffer[I])
  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => intListResult(Buffer[I] : .IntList, bwi(Buffer, I +Int 1))
      requires 0 <=Int I andBool I <Int lengthBytes(Buffer)
          andBool notBool bit8IsSet(Buffer[I])

  rule #parseLeb128IntChunks(Value:Int, intListResult(L:IntList, BWI:BytesWithIndex))
      => intListResult(Value : L, BWI)
  rule #parseLeb128IntChunks(_Value:Int, E:ParseError) => E


  syntax IntResult  ::= parseLeb128UInt(BytesWithIndex)  [function, total]
                      | #parseLeb128UInt(IntListResult)  [function, total]

  rule parseLeb128UInt(BWI:BytesWithIndex) => #parseLeb128UInt(parseLeb128IntChunks(BWI))
  rule #parseLeb128UInt(intListResult(L:IntList, BWI:BytesWithIndex))
      => intResult(buildLeb128UInt(L), BWI)
  rule #parseLeb128UInt(E:ParseError) => E

  syntax Int ::= buildLeb128UInt(IntList) [function, total]
  rule buildLeb128UInt(.IntList) => 0
  rule buildLeb128UInt(Value:Int : L:IntList) => Value +Int 128 *Int buildLeb128UInt(L)

```

  Extracting a numberr of bytes.

```k

  syntax BytesResult ::= bytesResult(Bytes, BytesWithIndex) | ParseError
  syntax BytesResult ::= parseBytes(BytesWithIndex, Int)  [function, total]
  rule parseBytes(bwi(Buffer:Bytes, Index:Int), Count:Int)
      => bytesResult
            ( substrBytes(Buffer, Index, Index +Int Count)
            , bwi(Buffer, Index +Int Count)
            )
      requires Index +Int Count <=Int lengthBytes(Buffer)
  rule parseBytes(bwi(Buffer:Bytes, Index:Int), Count:Int)
      => parseError("parseBytes", ListItem(lengthBytes(Buffer)) ListItem(Index) ListItem(Count) ListItem(Buffer))
      [owise]

```

  Skiping over some specific bytes.

```k

  syntax BytesWithIndexOrError ::= parseConstant(BytesWithIndexOrError, Bytes)  [function, total]
  rule parseConstant(bwi(Buffer:Bytes, Index:Int), Constant:Bytes)
      => bwi(Buffer, Index +Int lengthBytes(Constant))
      requires Index +Int lengthBytes(Constant) <=Int lengthBytes(Buffer)
          andBool substrBytes(Buffer, Index, Index +Int lengthBytes(Constant)) ==K Constant
  rule parseConstant(bwi(Buffer:Bytes, Index:Int), Constant:Bytes)
      => parseError("parseConstant", ListItem(lengthBytes(Buffer)) ListItem(Index) ListItem(Constant) ListItem(Buffer))
      [owise]
  rule parseConstant(E:ParseError, _:Bytes) => E

endmodule
```
