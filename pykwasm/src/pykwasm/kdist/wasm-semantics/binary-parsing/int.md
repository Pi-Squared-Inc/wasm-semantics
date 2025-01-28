  See the [LEB128 encoding](https://en.wikipedia.org/wiki/LEB128) for more details.

```k
module BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports  WASM-DATA-COMMON

  syntax IntResult ::= intResult(value:Int, remainder:BytesWithIndex) | ParseError
  syntax IntResult  ::= parseLeb128UInt(BytesWithIndex)  [function, total]
  syntax IntResult  ::= parseLeb128SInt(BytesWithIndex)  [function, total]
  syntax IntResult  ::= parseByteAsInt(BytesWithIndex)  [function, total]

  syntax IntsResult ::= intsResult(Ints, BytesWithIndex) | ParseError
  syntax IntsResult ::= parseUnsignedIntVec(BytesWithIndex)  [function, total]

  syntax BytesWithIndexOrError ::= ignoreUnsignedInt(BytesWithIndex, Int)  [function, total]
endmodule

module BINARY-PARSER-INT  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BOOL

  syntax Bool ::= bit8IsSet(Int) [function, total]
  rule bit8IsSet(I:Int) => I &Int 128 =/=Int 0

  syntax Int ::= clearBit8(Int) [function, total]
  rule clearBit8(I:Int) => I -Int 128 requires 128 <=Int I
  rule clearBit8(I:Int) => I requires I <Int 128

  syntax IntsResult ::= parseLeb128IntChunks(BytesWithIndex) [function, total]
                      | #parseLeb128IntChunks(Int, IntsResult) [function, total]

  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => parseError("parseLeb128IntChunks", ListItem(lengthBytes(Buffer)) ListItem(I) ListItem(Buffer))
      requires I <Int 0 orBool lengthBytes(Buffer) <=Int I
  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => #parseLeb128IntChunks(clearBit8(Buffer[I]), parseLeb128IntChunks(bwi(Buffer, I +Int 1)))
      requires 0 <=Int I andBool I <Int lengthBytes(Buffer)
          andBool bit8IsSet(Buffer[I])
  rule parseLeb128IntChunks(bwi(Buffer:Bytes, I:Int))
      => intsResult(Buffer[I] .Ints, bwi(Buffer, I +Int 1))
      requires 0 <=Int I andBool I <Int lengthBytes(Buffer)
          andBool notBool bit8IsSet(Buffer[I])

  rule #parseLeb128IntChunks(Value:Int, intsResult(L:Ints, BWI:BytesWithIndex))
      => intsResult(Value L, BWI)
  rule #parseLeb128IntChunks(_Value:Int, E:ParseError) => E


  syntax IntResult  ::= #parseLeb128UInt(IntsResult)  [function, total]

  rule parseLeb128UInt(BWI:BytesWithIndex) => #parseLeb128UInt(parseLeb128IntChunks(BWI))
  rule #parseLeb128UInt(intsResult(L:Ints, BWI:BytesWithIndex))
      => intResult(buildLeb128UInt(L), BWI)
  rule #parseLeb128UInt(E:ParseError) => E

  syntax IntResult  ::= #parseLeb128SInt(IntsResult)  [function, total]

  rule parseLeb128SInt(BWI:BytesWithIndex) => #parseLeb128SInt(parseLeb128IntChunks(BWI))
  rule #parseLeb128SInt(intsResult(L:Ints, BWI:BytesWithIndex))
      => intResult(leb128UnsignedToSigned(buildLeb128UInt(L), #lenInts(L) *Int 7), BWI)
  rule #parseLeb128SInt(E:ParseError) => E

  syntax Int ::= buildLeb128UInt(Ints) [function, total]
  rule buildLeb128UInt(.Ints) => 0
  rule buildLeb128UInt(Value:Int L:Ints) => Value +Int 128 *Int buildLeb128UInt(L)

  syntax Int ::= leb128UnsignedToSigned(unsigned: Int, bits: Int)  [function, total]
  rule leb128UnsignedToSigned(U:Int, Bits:Int) => U
      requires U <Int (1 <<Int (Bits -Int 1))
  rule leb128UnsignedToSigned(U:Int, Bits:Int) => U -Int (1 <<Int Bits)
      [owise]

  rule ignoreUnsignedInt(BWI:BytesWithIndex, Count:Int)
      => #ignoreUnsignedInt(Count -Int 1, parseLeb128UInt(BWI:BytesWithIndex))
      requires Count >Int 0
  rule ignoreUnsignedInt(BWI:BytesWithIndex, 0) => BWI
  rule ignoreUnsignedInt(BWI:BytesWithIndex, Count:Int)
      => parseError("ignoreUnsignedInt", ListItem(Count) ListItem(BWI))
      requires Count <Int 0

  syntax BytesWithIndexOrError ::= #ignoreUnsignedInt(Int, IntResult)  [function, total]
  rule #ignoreUnsignedInt(Count:Int, intResult(_:Int, BWI:BytesWithIndex))
      => ignoreUnsignedInt(BWI, Count)
  rule #ignoreUnsignedInt(_:Int, E:ParseError) => E

  rule parseByteAsInt(bwi(B:Bytes, Index:Int))
      => intResult(B[Index], bwi(B, Index +Int 1))
      requires 0 <=Int Index andBool Index <=Int lengthBytes(B)
  rule parseByteAsInt(bwi(B:Bytes, Index:Int))
      => parseError("parseByteAsInt", ListItem(Index) ListItem(lengthBytes(B)) ListItem(B))
      [owise]

  syntax IntsResult ::= #parseUnsignedIntVec1(IntResult) [function, total]
                      | #parseUnsignedIntVec2(count: Int, Ints, BytesWithIndex) [function, total]
                      | #parseUnsignedIntVec3(count: Int, Ints, IntResult) [function, total]

  rule parseUnsignedIntVec(BWI:BytesWithIndex) => #parseUnsignedIntVec1(parseLeb128UInt(BWI))
  rule #parseUnsignedIntVec1(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseUnsignedIntVec2(Count, .Ints, BWI)
  rule #parseUnsignedIntVec1(E:ParseError) => E
  rule #parseUnsignedIntVec2(0, L:Ints, BWI:BytesWithIndex)
      => intsResult(#reverseInts(L), BWI)
  rule #parseUnsignedIntVec2(Count:Int, L:Ints, BWI:BytesWithIndex)
      => #parseUnsignedIntVec3(Count -Int 1, L, parseLeb128UInt(BWI))
      requires Count >Int 0
  rule #parseUnsignedIntVec2(Count:Int, L:Ints, BWI:BytesWithIndex)
      => parseError("parseUnsignedIntVec2", ListItem(Count) ListItem(L) ListItem(BWI))
  rule #parseUnsignedIntVec3(Count:Int, L:Ints, intResult(Value:Int, BWI:BytesWithIndex))
      => #parseUnsignedIntVec2(Count, Value L, BWI)
  rule #parseUnsignedIntVec3(_Count:Int, _:Ints, E:ParseError) => E

endmodule
```
