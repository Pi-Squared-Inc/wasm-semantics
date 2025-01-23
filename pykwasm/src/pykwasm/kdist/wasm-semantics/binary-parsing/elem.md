Parsing an [element](https://webassembly.github.io/spec/core/binary/modules.html#binary-elemsec).

```k
module BINARY-PARSER-ELEM-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports LIST-REF
  imports WASM
  imports WASM-DATA-COMMON-SYNTAX

  syntax BinaryDefnElements ::= List{BinaryDefnElem, ""}

  syntax BinaryElemMode ::= #binaryElemActive( table: Int, offset: BinaryInstrs )
  syntax BinaryDefnElem ::= #binaryElem
            ( type: RefValType
            , elemSegment: ListRef
            , mode: BinaryElemMode
            )
  syntax BinaryDefn ::= BinaryDefnElem
  syntax DefnResult  ::= parseDefnElem(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-ELEM  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-ELEM-SYNTAX
  imports BINARY-PARSER-EXPR-SYNTAX
  imports BINARY-PARSER-EXPR-VEC-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-REFTYPE-SYNTAX
  imports BINARY-PARSER-TAGS

  syntax DefnResult ::= #parseDefnElem(IntResult)  [function, total]
  rule parseDefnElem(BWI:BytesWithIndex) => #parseDefnElem(parseLeb128UInt(BWI))
  rule #parseDefnElem(intResult(ELTS_ACTIVE_ZERO_BY_REF, BWI:BytesWithIndex)) => parseElem0(BWI)
  rule #parseDefnElem(intResult(ELTS_PASSIVE_BY_REF, BWI:BytesWithIndex)) => parseElem1(BWI)
  rule #parseDefnElem(intResult(ELTS_ACTIVE_IDX_BY_REF, BWI:BytesWithIndex)) => parseElem2(BWI)
  rule #parseDefnElem(intResult(ELTS_DECL_BY_REF, BWI:BytesWithIndex)) => parseElem3(BWI)
  rule #parseDefnElem(intResult(ELTS_ACTIVE_ZERO_BY_VAL, BWI:BytesWithIndex)) => parseElem4(BWI)
  rule #parseDefnElem(intResult(ELTS_PASSIVE_BY_VAL, BWI:BytesWithIndex)) => parseElem5(BWI)
  rule #parseDefnElem(intResult(ELTS_ACTIVE_IDX_BY_VAL, BWI:BytesWithIndex)) => parseElem6(BWI)
  rule #parseDefnElem(intResult(ELTS_DECL_BY_VAL, BWI:BytesWithIndex)) => parseElem7(BWI)
  rule #parseDefnElem(intResult(I:Int, BWI:BytesWithIndex)) => parseError("#parseDefnElem", ListItem(I) ListItem(BWI))
      [owise]
  rule #parseDefnElem(E:ParseError) => E

  syntax DefnResult ::= parseElem0(BytesWithIndex)  [function, total]
                      | #parseElem0a(ExprResult)  [function, total]
                      | #parseElem0b(BinaryInstrs, IntsResult)  [function, total]
  rule parseElem0(BWI:BytesWithIndex) => #parseElem0a(parseExpr(BWI))
  rule #parseElem0a(exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseElem0b(Is, parseUnsignedIntVec(BWI))
  rule #parseElem0a(E:ParseError) => E
  rule #parseElem0b(E:BinaryInstrs, intsResult(L:Ints, BWI:BytesWithIndex))
      => defnResult
          ( #binaryElem
              (... type: funcref
              , elemSegment: intsToRefFunc(L)
              , mode: #binaryElemActive(... table: 0, offset: E)
              )
          , BWI
          )
  rule #parseElem0b(_, E:ParseError) => E


  syntax DefnResult ::= parseElem1(BytesWithIndex)  [function, total]
                      | #parseElem1a(BytesWithIndexOrError)  [function, total]
                      | #parseElem1b(IntsResult)  [function, total]
  rule parseElem1(BWI:BytesWithIndex) => #parseElem1a(parseConstant(BWI, b"\x00"))
  rule #parseElem1a(BWI:BytesWithIndex) => #parseElem1b(parseUnsignedIntVec(BWI))
  rule #parseElem1a(E:ParseError) => E
  rule #parseElem1b(intsResult(L:Ints, BWI:BytesWithIndex))
      => defnResult
          ( #elem
              (... type: funcref
              , elemSegment: intsToRefFunc(L)
              , mode: #elemPassive
              , oid:
              )
          , BWI
          )
  rule #parseElem1b(E:ParseError) => E


  syntax DefnResult ::= parseElem2(BytesWithIndex)  [function, total]
                      | #parseElem2a(IntResult)  [function, total]
                      | #parseElem2b(Int, ExprResult)  [function, total]
                      | #parseElem2c(Int, BinaryInstrs, BytesWithIndexOrError)  [function, total]
                      | #parseElem2d(Int, BinaryInstrs, IntsResult)  [function, total]
  rule parseElem2(BWI:BytesWithIndex) => #parseElem2a(parseLeb128UInt(BWI))
  rule #parseElem2a(intResult(TableIdx:Int, BWI:BytesWithIndex))
      => #parseElem2b(TableIdx, parseExpr(BWI))
  rule #parseElem2a(E:ParseError) => E
  rule #parseElem2b(TableIdx:Int, exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseElem2c(TableIdx, Is, parseConstant(BWI, b"\x00"))
  rule #parseElem2b(_, E:ParseError) => E
  rule #parseElem2c(TableIdx:Int, Is:BinaryInstrs, BWI:BytesWithIndex)
      => #parseElem2d(TableIdx, Is, parseUnsignedIntVec(BWI))
  rule #parseElem2c(_, _, E:ParseError) => E
  rule #parseElem2d(TableIdx:Int, Is:BinaryInstrs, intsResult(L:Ints, BWI:BytesWithIndex))
      => defnResult
          ( #binaryElem
              (... type: funcref
              , elemSegment: intsToRefFunc(L)
              , mode: #binaryElemActive(... table: TableIdx, offset: Is)
              )
          , BWI
          )
  rule #parseElem2d(_, _, E:ParseError) => E


  syntax DefnResult ::= parseElem3(BytesWithIndex)  [function, total]
                      | #parseElem3a(BytesWithIndexOrError)  [function, total]
                      | #parseElem3b(IntsResult)  [function, total]
  rule parseElem3(BWI:BytesWithIndex) => #parseElem3a(parseConstant(BWI, b"\x00"))
  rule #parseElem3a(BWI:BytesWithIndex) => #parseElem3b(parseUnsignedIntVec(BWI))
  rule #parseElem3a(E:ParseError) => E
  rule #parseElem3b(intsResult(L:Ints, BWI:BytesWithIndex))
      => defnResult
          ( #elem
              (... type: funcref
              , elemSegment: intsToRefFunc(L)
              , mode: #elemDeclarative
              , oid:
              )
          , BWI
          )
  rule #parseElem3b(E:ParseError) => E


  syntax DefnResult ::= parseElem4(BytesWithIndex)  [function, total]
                      | #parseElem4a(ExprResult)  [function, total]
                      | #parseElem4b(BinaryInstrs, ExprVecResult)  [function, total]
  rule parseElem4(BWI:BytesWithIndex) => #parseElem4a(parseExpr(BWI))
  rule #parseElem4a(exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseElem4b(Is, parseExprVec(BWI))
  rule #parseElem4a(E:ParseError) => E
  rule #parseElem4b(E:BinaryInstrs, exprVecResult(Es:ExprVec, BWI:BytesWithIndex))
      => parseError("#parseElem4b: unimplemented", ListItem(E) ListItem(Es) ListItem(BWI))
  rule #parseElem4b(_, E:ParseError) => E


  syntax DefnResult ::= parseElem5(BytesWithIndex)  [function, total]
                      | #parseElem5a(RefTypeResult)  [function, total]
                      | #parseElem5b(RefValType, ExprVecResult)  [function, total]
  rule parseElem5(BWI:BytesWithIndex) => #parseElem5a(parseRefType(BWI))
  rule #parseElem5a(refTypeResult(T:RefValType, BWI:BytesWithIndex))
      => #parseElem5b(T, parseExprVec(BWI))
  rule #parseElem5a(E:ParseError) => E
  rule #parseElem5b(T:RefValType, exprVecResult(Es:ExprVec, BWI:BytesWithIndex))
      => parseError("#parseElem5b: unimplemented", ListItem(T) ListItem(Es) ListItem(BWI))
  rule #parseElem5b(_, E:ParseError) => E


  syntax DefnResult ::= parseElem6(BytesWithIndex)  [function, total]
                      | #parseElem6a(IntResult)  [function, total]
                      | #parseElem6b(Int, ExprResult)  [function, total]
                      | #parseElem6c(Int, BinaryInstrs, RefTypeResult)  [function, total]
                      | #parseElem6d(Int, BinaryInstrs, RefValType, ExprVecResult)  [function, total]
  rule parseElem6(BWI:BytesWithIndex) => #parseElem6a(parseLeb128UInt(BWI))
  rule #parseElem6a(intResult(TableIdx:Int, BWI:BytesWithIndex))
      => #parseElem6b(TableIdx, parseExpr(BWI))
  rule #parseElem6a(E:ParseError) => E
  rule #parseElem6b(TableIdx:Int, exprResult(Is:BinaryInstrs, BWI:BytesWithIndex))
      => #parseElem6c(TableIdx, Is, parseRefType(BWI))
  rule #parseElem6b(_, E:ParseError) => E
  rule #parseElem6c(TableIdx:Int, Is:BinaryInstrs, refTypeResult(T:RefValType, BWI:BytesWithIndex))
      => #parseElem6d(TableIdx, Is, T, parseExprVec(BWI))
  rule #parseElem6c(_, _, E:ParseError) => E
  rule #parseElem6d(TableIdx:Int, Is:BinaryInstrs, T:RefValType, exprVecResult(Es:ExprVec, BWI:BytesWithIndex))
      => parseError("#parseElem6d: unimplemented", ListItem(TableIdx) ListItem(Is) ListItem(T) ListItem(Es) ListItem(BWI))
  rule #parseElem6d(_, _, _, E:ParseError) => E


  syntax DefnResult ::= parseElem7(BytesWithIndex)  [function, total]
                      | #parseElem7a(RefTypeResult)  [function, total]
                      | #parseElem7b(RefValType, ExprVecResult)  [function, total]
  rule parseElem7(BWI:BytesWithIndex) => #parseElem7a(parseRefType(BWI))
  rule #parseElem7a(refTypeResult(T:RefValType, BWI:BytesWithIndex))
      => #parseElem7b(T, parseExprVec(BWI))
  rule #parseElem7a(E:ParseError) => E
  rule #parseElem7b(T:RefValType, exprVecResult(Es:ExprVec, BWI:BytesWithIndex))
      => parseError("#parseElem7b: unimplemented", ListItem(T) ListItem(Es) ListItem(BWI))
  rule #parseElem7b(_, E:ParseError) => E


  syntax ListRef ::= intsToRefFunc(Ints) [function, total]
  rule intsToRefFunc(.Ints) => .ListRef
  rule intsToRefFunc(I:Int Is:Ints) => ListItem(<funcref> I) intsToRefFunc(Is)

endmodule
```
