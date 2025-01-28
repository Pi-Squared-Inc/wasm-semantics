Extract a number of bytes from the buffer.

```k
module BINARY-PARSER-BYTES-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax BytesResult ::= bytesResult(Bytes, BytesWithIndex) | ParseError
  syntax BytesResult ::= parseBytes(BytesWithIndex, Int)  [function, total]

  syntax BytesWithIndexOrError ::= ignoreBytes(BytesWithIndex, Int)  [function, total]
endmodule

module BINARY-PARSER-BYTES  [private]
  imports BINARY-PARSER-BYTES-SYNTAX

  rule parseBytes(bwi(Buffer:Bytes, Index:Int), Count:Int)
      => bytesResult
            ( substrBytes(Buffer, Index, Index +Int Count)
            , bwi(Buffer, Index +Int Count)
            )
      requires Index +Int Count <=Int lengthBytes(Buffer)
  rule parseBytes(bwi(Buffer:Bytes, Index:Int), Count:Int)
      => parseError("parseBytes", ListItem(lengthBytes(Buffer)) ListItem(Index) ListItem(Count) ListItem(Buffer))
      [owise]

  rule ignoreBytes(BWI:BytesWithIndex, Count:Int)
      => #ignoreBytes(parseBytes(BWI, Count))

  syntax BytesWithIndexOrError ::= #ignoreBytes(BytesResult)  [function, total]
  rule #ignoreBytes(bytesResult(_:Bytes, BWI:BytesWithIndex)) => BWI
  rule #ignoreBytes(E:ParseError) => E
endmodule

```
