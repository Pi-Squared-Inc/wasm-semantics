Parsing [value types](https://webassembly.github.io/spec/core/binary/types.html#binary-valtype)
individually and as a vector.

```k

module BINARY-PARSER-VALTYPE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax ValTypeResult ::= valTypeResult(ValType, BytesWithIndex) | ParseError
  syntax ValTypeResult ::= parseValType(BytesWithIndex)  [function, total]

  syntax ValTypesResult ::= valTypesResult(ValTypes, BytesWithIndex) | ParseError
  syntax ValTypesResult ::= parseValTypes(remaining:Int, ValTypes, BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-VALTYPE  [private]
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax ValTypeResult  ::= #parseValTypeI32(BytesWithIndex, BytesWithIndexOrError)  [function, total]
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


  syntax ValTypesResult ::= #parseValTypes(remaining:Int, ValTypes, ValTypeResult)  [function, total]
  rule parseValTypes(0, V:ValTypes, BWI:BytesWithIndex)
      => valTypesResult(reverse(V), BWI)
  rule parseValTypes(Count:Int, V:ValTypes, BWI:BytesWithIndex)
      => #parseValTypes(Count -Int 1, V, parseValType(BWI))
      requires Count >Int 0
  rule parseValTypes(Count:Int, V:ValTypes, bwi(B:Bytes, I:Int))
      => parseError("parseValTypes", ListItem(Count) ListItem(V) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseValTypes(Count:Int, Vs:ValTypes, valTypeResult(V:ValType, BWI:BytesWithIndex))
      => parseValTypes(Count, V Vs, BWI)
  rule #parseValTypes(_:Int, _:ValTypes, E:ParseError) => E

  syntax ValTypes ::= reverse(ValTypes)  [function, total]
                    | #reverse(ValTypes, ValTypes)  [function, total]
  rule reverse(V:ValTypes) => #reverse(V, .ValTypes)
  rule #reverse(.ValTypes, Vs:ValTypes) => Vs
  rule #reverse(V:ValType Vs1:ValTypes, Vs2:ValTypes) => #reverse(Vs1, V Vs2)

endmodule

```