// Parsing an [import](https://webassembly.github.io/spec/core/binary/modules.html#binary-importsec).

```k
module BINARY-PARSER-DATA-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX

  syntax DefnKind ::= "defnData"

  syntax BinaryDefnDatas ::= List{BinaryDefnData, ""}

  syntax BinaryDefnData ::= #binaryData
                                ( index: Int
                                , offset: BinaryInstrs
                                , data: Bytes
                                )
  syntax BinaryDefn ::= BinaryDefnData

endmodule

module BINARY-PARSER-DATA  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-BYTES-SYNTAX
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-DATA-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-TAGS

  rule parseDefn(defnData, BWI:BytesWithIndex) => parseDefnData(BWI)

  syntax DefnResult ::= parseDefnData(BytesWithIndex)  [function, total]
                      | #parseDefnData(IntResult)  [function, total]
  rule parseDefnData(BWI:BytesWithIndex) => #parseDefnData(parseLeb128UInt(BWI))
  rule #parseDefnData(intResult(DATA_ACTIVE_ZERO, BWI:BytesWithIndex)) => parseDefnDataActive(BWI)
  rule #parseDefnData(intResult(DATA_PASSIVE, BWI:BytesWithIndex)) => parseDefnDataPassive(BWI)
  rule #parseDefnData(intResult(DATA_ACTIVE_IDX, BWI:BytesWithIndex)) => parseDefnDataActiveIdx(BWI)
  rule #parseDefnData(intResult(I:Int, BWI:BytesWithIndex))
      => parseError("#parseDefnData", ListItem(I) ListItem(BWI))
      [owise]
  rule #parseDefnData(E:ParseError) => E

  syntax DefnResult ::= parseDefnDataActive(BytesWithIndex)  [function, total]
                      | #parseDefnDataActive1(ExprResult)  [function, total]
                      | #parseDefnDataActive2(BinaryInstrs, IntResult)  [function, total]
                      | #parseDefnDataActive3(BinaryInstrs, BytesResult)  [function, total]
  rule parseDefnDataActive(BWI:BytesWithIndex) => #parseDefnDataActive1(parseExpr(BWI))
  rule #parseDefnDataActive1(exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseDefnDataActive2(Is, parseLeb128UInt(BWI))
  rule #parseDefnDataActive1(E:ParseError) => E
  rule #parseDefnDataActive2(Is:BinaryInstrs, intResult(Count:Int, BWI:BytesWithIndex))
      => #parseDefnDataActive3(Is, parseBytes(BWI, Count))
  rule #parseDefnDataActive2(_:BinaryInstrs, E:ParseError) => E
  rule #parseDefnDataActive3(Is:BinaryInstrs, bytesResult(B:Bytes, BWI:BytesWithIndex))
      => defnResult(#binaryData(... index: 0, offset: Is, data: B), BWI)
  rule #parseDefnDataActive3(_:BinaryInstrs, E:ParseError) => E

  syntax DefnResult ::= parseDefnDataPassive(BytesWithIndex)  [function, total]
                      | #parseDefnDataPassive1(IntResult)  [function, total]
                      | #parseDefnDataPassive2(BytesResult)  [function, total]
  rule parseDefnDataPassive(BWI:BytesWithIndex) => #parseDefnDataPassive1(parseLeb128UInt(BWI))
  rule #parseDefnDataPassive1(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseDefnDataPassive2(parseBytes(BWI, Count))
  rule #parseDefnDataPassive1(E:ParseError) => E
  rule #parseDefnDataPassive2(bytesResult(B:Bytes, BWI:BytesWithIndex))
      => defnResult(#binaryData(... index: 0, offset: .BinaryInstrs, data: B), BWI)
  rule #parseDefnDataPassive2(E:ParseError) => E

  syntax DefnResult ::= parseDefnDataActiveIdx(BytesWithIndex)  [function, total]
                      | #parseDefnDataActiveIdx1(IntResult)  [function, total]
                      | #parseDefnDataActiveIdx2(memIdx: Int, ExprResult)  [function, total]
                      | #parseDefnDataActiveIdx3(memIdx: Int, BinaryInstrs, IntResult)  [function, total]
                      | #parseDefnDataActiveIdx4(memIdx: Int, BinaryInstrs, BytesResult)  [function, total]
  rule parseDefnDataActiveIdx(BWI:BytesWithIndex) => #parseDefnDataActiveIdx1(parseLeb128UInt(BWI))
  rule #parseDefnDataActiveIdx1(intResult(MemIdx:Int, BWI:BytesWithIndex))
      => #parseDefnDataActiveIdx2(MemIdx, parseExpr(BWI))
  rule #parseDefnDataActiveIdx1(E:ParseError) => E
  rule #parseDefnDataActiveIdx2(MemIdx:Int, exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseDefnDataActiveIdx3(MemIdx, Is, parseLeb128UInt(BWI))
  rule #parseDefnDataActiveIdx2(_:Int, E:ParseError) => E
  rule #parseDefnDataActiveIdx3(MemIdx:Int, Is:BinaryInstrs, intResult(Count:Int, BWI:BytesWithIndex))
      => #parseDefnDataActiveIdx4(MemIdx, Is, parseBytes(BWI, Count))
  rule #parseDefnDataActiveIdx3(_:Int, _:BinaryInstrs, E:ParseError) => E
  rule #parseDefnDataActiveIdx4(MemIdx:Int, Is:BinaryInstrs, bytesResult(B:Bytes, BWI:BytesWithIndex))
      => defnResult(#binaryData(... index: MemIdx, offset: Is, data: B), BWI)
  rule #parseDefnDataActiveIdx4(_:Int, _:BinaryInstrs, E:ParseError) => E
endmodule
```
