  See the [LEB128 encoding](https://en.wikipedia.org/wiki/LEB128) for more details.

```k
module BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax IntResult ::= intResult(value:Int, remainder:BytesWithIndex) | ParseError
  syntax IntResult  ::= parseLeb128UInt(BytesWithIndex)  [function, total]

  // TODO: Rename to IntVec
  syntax IntList ::= List{Int, ":"}
  syntax IntListResult ::= intListResult(IntList, BytesWithIndex) | ParseError
endmodule

module BINARY-PARSER-INT  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BOOL

  syntax Bool ::= bit8IsSet(Int) [function, total]
  rule bit8IsSet(I:Int) => I &Int 128 =/=Int 0

  syntax Int ::= clearBit8(Int) [function, total]
  rule clearBit8(I:Int) => I ^Int (I &Int 128)

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


  syntax IntResult  ::= #parseLeb128UInt(IntListResult)  [function, total]

  rule parseLeb128UInt(BWI:BytesWithIndex) => #parseLeb128UInt(parseLeb128IntChunks(BWI))
  rule #parseLeb128UInt(intListResult(L:IntList, BWI:BytesWithIndex))
      => intResult(buildLeb128UInt(L), BWI)
  rule #parseLeb128UInt(E:ParseError) => E

  syntax Int ::= buildLeb128UInt(IntList) [function, total]
  rule buildLeb128UInt(.IntList) => 0
  rule buildLeb128UInt(Value:Int : L:IntList) => Value +Int 128 *Int buildLeb128UInt(L)

endmodule
```