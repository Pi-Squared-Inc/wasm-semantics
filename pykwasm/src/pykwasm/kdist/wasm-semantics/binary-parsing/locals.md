// Parsing a [locals object](https://webassembly.github.io/spec/core/binary/modules.html#binary-local).

```k
module BINARY-PARSER-LOCALS-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON-SYNTAX

  syntax Locals ::= locals(Int, ValType)
  syntax LocalsResult ::= localsResult(Locals, BytesWithIndex) | ParseError
  syntax LocalsResult ::= parseLocals(BytesWithIndex)  [function, total]

  syntax LocalsVec ::= List{Locals, ","}
  syntax LocalsVecResult ::= localsVecResult(LocalsVec, BytesWithIndex) | ParseError
  syntax LocalsVecResult ::= parseLocalsVec(BytesWithIndex)  [function, total]

  syntax ValTypes ::= localsVecToValTypes(LocalsVec)  [function, total]
endmodule

module BINARY-PARSER-LOCALS  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-LOCALS-SYNTAX
  imports BINARY-PARSER-VALTYPE-SYNTAX

  syntax LocalsResult ::= #parseLocals1(IntResult)  [function, total]
                        | #parseLocals2(Int, ValTypeResult)  [function, total]

  rule parseLocals(BWI:BytesWithIndex) => #parseLocals1(parseLeb128UInt(BWI))
  rule #parseLocals1(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseLocals2(Count, parseValType(BWI))
  rule #parseLocals1(E:ParseError) => E
  rule #parseLocals2(I:Int, valTypeResult(T:ValType, BWI:BytesWithIndex))
      => localsResult(locals(I, T), BWI)
  rule #parseLocals2(_, E:ParseError) => E

  syntax LocalsVecResult ::= #parseLocalsVec1(IntResult)  [function, total]
                            | #parseLocalsVec2(LocalsVec, Int, BytesWithIndex)  [function, total]
                            | #parseLocalsVec3(LocalsVec, Int, LocalsResult)  [function, total]

  rule parseLocalsVec(BWI:BytesWithIndex) => #parseLocalsVec1(parseLeb128UInt(BWI))
  rule #parseLocalsVec1(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseLocalsVec2(.LocalsVec, Count, BWI)
  rule #parseLocalsVec1(E:ParseError) => E

  rule #parseLocalsVec2(L:LocalsVec, Count:Int, BWI:BytesWithIndex)
      => parseError("#parseLocalsVec2", ListItem(Count) ListItem(L) ListItem(BWI))
      requires Count <Int 0
  rule #parseLocalsVec2(L:LocalsVec, 0, BWI:BytesWithIndex)
      => localsVecResult(reverse(L), BWI)
  rule #parseLocalsVec2(L:LocalsVec, Count:Int, BWI:BytesWithIndex)
      => #parseLocalsVec3(L, Count -Int 1, parseLocals(BWI))
      requires Count >Int 0

  rule #parseLocalsVec3(Ls:LocalsVec, Count:Int, localsResult(L:Locals, BWI:BytesWithIndex))
      => #parseLocalsVec2((L , Ls), Count, BWI)
  rule #parseLocalsVec3(_:LocalsVec, _:Int, E:ParseError) => E

  syntax LocalsVec ::= reverse(LocalsVec)  [function, total]
                      | #reverse(LocalsVec, LocalsVec)  [function, total]

  rule reverse(L:LocalsVec) => #reverse(L, .LocalsVec)
  rule #reverse(.LocalsVec, L:LocalsVec) => L
  rule #reverse((L:Locals , L1:LocalsVec), L2:LocalsVec) => #reverse(L1, (L , L2))

  rule localsVecToValTypes(.LocalsVec) => .ValTypes
  rule localsVecToValTypes(locals(Count:Int, _T:ValType) , Ls:LocalsVec)
      => localsVecToValTypes(Ls)
      requires Count <=Int 0
  rule localsVecToValTypes(locals(Count:Int, T:ValType) , Ls:LocalsVec)
      => T localsVecToValTypes(locals(Count -Int 1, T) , Ls)
      requires Count >Int 0
endmodule
```
