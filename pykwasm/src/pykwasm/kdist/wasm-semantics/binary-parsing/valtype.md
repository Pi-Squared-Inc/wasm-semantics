Parsing [value types](https://webassembly.github.io/spec/core/binary/types.html#binary-valtype)
individually and as a vector.

```k

module BINARY-PARSER-VALTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax ValTypeResult ::= valTypeResult(ValType, BytesWithIndex) | ParseError
  syntax ValTypeResult ::= parseValType(BytesWithIndex)  [function, total]

  syntax ValTypesResult ::= valTypesResult(ValTypes, BytesWithIndex) | ParseError
  syntax ValTypesResult ::= parseValTypes(BytesWithIndex)  [function, total]

```

  Sometimes (see ref.null) we neef to parse a value type as a heap type.

```k
  syntax HeapTypeResult ::= heapTypeResult(HeapType, BytesWithIndex) | ParseError
  syntax HeapTypeResult ::= parseHeapType(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-VALTYPE  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-REFTYPE-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax ValTypeResult  ::= #parseValTypeI32(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeI64(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeF32(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeF64(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeVec(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseValTypeRef(RefTypeResult)  [function, total]

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
      => #parseValTypeRef(parseRefType(BWI))
  rule #parseValTypeRef(refTypeResult(T:RefValType, BWI:BytesWithIndex))
      => valTypeResult(T, BWI)
  rule #parseValTypeRef(E:ParseError) => E


  syntax ValTypesResult ::= #parseValTypes1(IntResult)  [function, total]
  syntax ValTypesResult ::= #parseValTypes2(remaining:Int, ValTypes, BytesWithIndex)  [function, total]
  syntax ValTypesResult ::= #parseValTypes3(remaining:Int, ValTypes, ValTypeResult)  [function, total]

  rule parseValTypes(BWI:BytesWithIndex)
      => #parseValTypes1(parseLeb128UInt(BWI))
  rule #parseValTypes1(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseValTypes2(Count, .ValTypes, BWI)
  rule #parseValTypes1(E:ParseError) => E
  rule #parseValTypes2(0, V:ValTypes, BWI:BytesWithIndex)
      => valTypesResult(reverse(V), BWI)
  rule #parseValTypes2(Count:Int, V:ValTypes, BWI:BytesWithIndex)
      => #parseValTypes3(Count -Int 1, V, parseValType(BWI))
      requires Count >Int 0
  rule #parseValTypes2(Count:Int, V:ValTypes, bwi(B:Bytes, I:Int))
      => parseError("#parseValTypes2", ListItem(Count) ListItem(V) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseValTypes3(Count:Int, Vs:ValTypes, valTypeResult(V:ValType, BWI:BytesWithIndex))
      => #parseValTypes2(Count, V Vs, BWI)
  rule #parseValTypes3(_:Int, _:ValTypes, E:ParseError) => E

  syntax ValTypes ::= reverse(ValTypes)  [function, total]
                    | #reverse(ValTypes, ValTypes)  [function, total]
  rule reverse(V:ValTypes) => #reverse(V, .ValTypes)
  rule #reverse(.ValTypes, Vs:ValTypes) => Vs
  rule #reverse(V:ValType Vs1:ValTypes, Vs2:ValTypes) => #reverse(Vs1, V Vs2)

  syntax HeapTypeResult ::= #parseHeapTypeFuncRef(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                          | #parseHeapTypeExtRef(BytesWithIndex, BytesWithIndexOrError)  [function, total]
  rule parseHeapType(BWI:BytesWithIndex)
      => #parseHeapTypeFuncRef(BWI, parseConstant(BWI, TYPE_FUN_REF))
  rule #parseHeapTypeFuncRef(_, BWI:BytesWithIndex) => heapTypeResult(func, BWI)
  rule #parseHeapTypeFuncRef(BWI:BytesWithIndex, _:ParseError)
      => #parseHeapTypeExtRef(BWI, parseConstant(BWI, TYPE_EXT_REF))
  rule #parseHeapTypeExtRef(_, BWI:BytesWithIndex) => heapTypeResult(extern, BWI)
  rule #parseHeapTypeExtRef(_:BytesWithIndex, E:ParseError)
      => E

endmodule

```