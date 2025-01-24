Convert BinaryDefn to Defn.

```k
module BINARY-PARSER-BINARY-DEFN-CONVERT-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-ELEM-SYNTAX
  imports BINARY-PARSER-GLOBAL-SYNTAX
  imports BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports WASM-DATA-COMMON

  syntax DefnsOrError ::= buildFunctionDefns(Defns, BinaryDefnFunctionTypes, BinaryDefnFunctionBodies)  [function, total]
  syntax DefnsOrError ::= buildElementDefns(Defns, BinaryDefnElements)  [function, total]
  syntax DefnsOrError ::= buildGlobalDefns(Defns, BinaryDefnGlobals)  [function, total]

endmodule

module BINARY-PARSER-BINARY-DEFN-CONVERT  [private]
  imports BINARY-PARSER-BINARY-DEFN-CONVERT-SYNTAX
  imports BINARY-PARSER-BLOCK-SYNTAX
  imports BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-LOOP-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports WASM

  syntax DefnsOrError ::= #buildFunctionDefns1
                              ( DefnOrError
                              , Defns
                              , BinaryDefnFunctionTypes
                              , BinaryDefnFunctionBodies
                              )  [function, total]
                        | #buildFunctionDefns2(Defn, DefnsOrError)  [function, total]
  rule buildFunctionDefns(_:Defns, .BinaryDefnFunctionTypes, .BinaryDefnFunctionBodies)
      => .Defns
  rule buildFunctionDefns
          ( Ds:Defns
          , FT:BinaryDefnFunctionType FTs:BinaryDefnFunctionTypes
          , FB:BinaryDefnFunctionBody FBs:BinaryDefnFunctionBodies
          )
      => #buildFunctionDefns1(buildFunctionDefn(Ds, FT, FB), Ds, FTs, FBs)
  rule buildFunctionDefns(Ds:Defns, FTs:BinaryDefnFunctionTypes, FBs:BinaryDefnFunctionBodies)
      => parseError("buildFunctionDefns", ListItem(Ds) ListItem(FTs) ListItem(FBs))
      [owise]
  rule #buildFunctionDefns1
          ( D:Defn
          , Ds:Defns
          , FTs:BinaryDefnFunctionTypes
          , FBs:BinaryDefnFunctionBodies
          )
      => #buildFunctionDefns2(D, buildFunctionDefns(Ds, FTs, FBs))
  rule #buildFunctionDefns1
          ( E:ParseError
          , _:Defns
          , _:BinaryDefnFunctionTypes
          , _:BinaryDefnFunctionBodies
          )
      => E
  rule #buildFunctionDefns2(D:Defn, Ds:Defns) => D Ds
  rule #buildFunctionDefns2(_:Defn, E:ParseError) => E

  syntax DefnOrError  ::= buildFunctionDefn
                              ( Defns
                              , BinaryDefnFunctionType
                              , BinaryDefnFunctionBody
                              )  [function, total]
                        | #buildFunctionDefn1
                              ( BinaryDefnFunctionType
                              , locals: VecType
                              , InstrsOrError
                              )  [function, total]

  rule buildFunctionDefn
          ( Ds:Defns
          , FT:BinaryDefnFunctionType
          , binaryDefnFunctionBody(Locals:VecType, Is:BinaryInstrs)
          )
      => #buildFunctionDefn1(FT, Locals, binaryInstrsToInstrs(Ds, Is))
  rule #buildFunctionDefn1(binaryDefnFunctionType(TypeIndex:Int), Locals:VecType, Is:Instrs)
      => #func(TypeIndex, Locals, Is, #meta(, .Map))
  rule #buildFunctionDefn1(_:BinaryDefnFunctionType, _Locals:VecType, E:ParseError) => E

  syntax InstrsOrError  ::= binaryInstrsToInstrs(Defns, BinaryInstrs)  [function, total]
                          | #binaryInstrsToInstrs(InstrOrError, InstrsOrError)  [function, total]
  rule binaryInstrsToInstrs(_:Defns, .BinaryInstrs) => .Instrs
  rule binaryInstrsToInstrs(Ds:Defns, I:BinaryInstr Is:BinaryInstrs)
      => #binaryInstrsToInstrs(binaryInstrToInstr(Ds, I), binaryInstrsToInstrs(Ds, Is))
  rule #binaryInstrsToInstrs(I:Instr, Is:Instrs) => I Is
  rule #binaryInstrsToInstrs(E:ParseError, _:InstrsOrError) => E
  rule #binaryInstrsToInstrs(_:Instr, E:ParseError) => E

  syntax InstrOrError ::= binaryInstrToInstr(Defns, BinaryInstr)  [function, total]
  rule binaryInstrToInstr(_Ds:Defns, I:Instr) => I
  rule binaryInstrToInstr(Ds:Defns, B:Block)
      => resolvedBlockToInstr(resolveBlock(Ds, B))
  rule binaryInstrToInstr(Ds:Defns, loop(B:Block))
      => resolvedBlockToLoop(resolveBlock(Ds, B))
  rule binaryInstrToInstr(Ds:Defns, if(B:Block, Is:BinaryInstrs))
      => resolvedBlockInstrsToIf(resolveBlock(Ds, B), binaryInstrsToInstrs(Ds, Is))

  syntax VecTypeOrError ::= VecType | ParseError

  syntax ResolvedBlockOrError ::= resolvedBlock(VecType, Instrs) | ParseError

  syntax ResolvedBlockOrError ::= resolveBlock(Defns, Block)  [function, total]
                                | #resolveBlock(VecTypeOrError, InstrsOrError)  [function, total]
  rule resolveBlock(Ds:Defns, block(T:BlockType, Is:BinaryInstrs))
      => #resolveBlock(blockTypeToVecType(T, Ds), binaryInstrsToInstrs(Ds, Is))
  rule #resolveBlock(T:VecType, Is:Instrs) => resolvedBlock(T, Is)
  rule #resolveBlock(E:ParseError, _:InstrsOrError) => E
  rule #resolveBlock(_:VecType, E:ParseError) => E

  syntax InstrOrError ::= resolvedBlockToInstr(ResolvedBlockOrError)  [function, total]
  rule resolvedBlockToInstr(resolvedBlock(T:VecType, Is:Instrs)) => #block(T, Is, .Int)
  rule resolvedBlockToInstr(E:ParseError) => E

  syntax InstrOrError ::= resolvedBlockToLoop(ResolvedBlockOrError)  [function, total]
  rule resolvedBlockToLoop(resolvedBlock(T:VecType, Is:Instrs)) => #loop(T, Is, .Int)
  rule resolvedBlockToLoop(E:ParseError) => E

  syntax InstrOrError ::= resolvedBlockInstrsToIf(ResolvedBlockOrError, InstrsOrError)  [function, total]
  rule resolvedBlockInstrsToIf(resolvedBlock(T:VecType, Then:Instrs), Else:Instrs) => #if(T, Then, Else, .Int)
  rule resolvedBlockInstrsToIf(E:ParseError, _:InstrsOrError) => E
  rule resolvedBlockInstrsToIf(_:ResolvedBlockOrError, E:ParseError) => E
      [owise]


  syntax DefnsOrError ::= #buildElementDefns1(DefnOrError, DefnsOrError)  [function, total]
  rule buildElementDefns(_:Defns, .BinaryDefnElements) => .Defns
  rule buildElementDefns
          ( Ds:Defns
          , E:BinaryDefnElem Es:BinaryDefnElements
          )
      => #buildElementDefns1(buildElementDefn(Ds, E), buildElementDefns(Ds, Es))
  rule #buildElementDefns1(D:Defn, Ds:Defns) => D Ds
  rule #buildElementDefns1(E:ParseError, _:DefnsOrError) => E
  rule #buildElementDefns1(_:Defn, E:ParseError) => E

  syntax DefnOrError  ::= buildElementDefn(Defns, BinaryDefnElem)  [function, total]
                        | #buildElementDefn(RefValType, ListRef, Int, InstrsOrError)  [function, total]
  rule buildElementDefn
          ( Ds:Defns
          , #binaryElem
              ( T:RefValType
              , Segment:ListRef
              , #binaryElemActive(Table:Int, Offset:BinaryInstrs)
              )
          )
      => #buildElementDefn(T, Segment, Table, binaryInstrsToInstrs(Ds, Offset))
  rule #buildElementDefn(T:RefValType, Segment:ListRef, Table:Int, Is:Instrs)
      => #elem(T, Segment, #elemActive(Table, Is), )
  rule #buildElementDefn(_:RefValType, _:ListRef, _:Int, E:ParseError) => E


  syntax DefnsOrError ::= #buildGlobalDefns1(DefnOrError, DefnsOrError)  [function, total]
  rule buildGlobalDefns(_:Defns, .BinaryDefnGlobals) => .Defns
  rule buildGlobalDefns
          ( Ds:Defns
          , E:BinaryDefnGlobal Es:BinaryDefnGlobals
          )
      => #buildGlobalDefns1(buildGlobalDefn(Ds, E), buildGlobalDefns(Ds, Es))
  rule #buildGlobalDefns1(D:Defn, Ds:Defns) => D Ds
  rule #buildGlobalDefns1(E:ParseError, _:DefnsOrError) => E
  rule #buildGlobalDefns1(_:Defn, E:ParseError) => E

  syntax DefnOrError  ::= buildGlobalDefn(Defns, BinaryDefnGlobal)  [function, total]
                        | #buildGlobalDefn(GlobalType, InstrsOrError)  [function, total]
  rule buildGlobalDefn
          ( Ds:Defns
          , #binaryGlobal
              ( T:GlobalType
              , Is:BinaryInstrs
              )
          )
      => #buildGlobalDefn(T, binaryInstrsToInstrs(Ds, Is))
  rule #buildGlobalDefn(T:GlobalType, Is:Instrs) => #global(T, Is, )
  rule #buildGlobalDefn(_:GlobalType, E:ParseError) => E

endmodule
```
