[Module](https://webassembly.github.io/spec/core/binary/modules.html) parsing

```k
module BINARY-PARSER-MODULE-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax ModuleResult ::= moduleResult(ModuleDecl, BytesWithIndex) | ParseError

  syntax ModuleResult ::= parseModule(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-MODULE-TEST-SYNTAX
  imports BOOL-SYNTAX
  imports WASM

  syntax ModuleDecl ::= addDefnToModule(Bool, Defn, ModuleDecl)  [function, total]
endmodule

module BINARY-PARSER-MODULE  [private]
  imports BINARY-PARSER-BINARY-DEFN-CONVERT-SYNTAX
  imports BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-ELEM-SYNTAX
  imports BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports BINARY-PARSER-MODULE-SYNTAX
  imports BINARY-PARSER-MODULE-TEST-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-SYNTAX
  imports BINARY-PARSER-TAGS

  rule parseModule(BWI:BytesWithIndex)
      => parseModuleSections(reverseSections(splitSections(parseConstant(parseConstant(BWI, MAGIC), VERSION))))

  syntax ModuleResult ::= parseModuleSections(UnparsedSectionsResult)  [function, total]
                        | #parseModuleSections1(ParsedSectionsResult, BytesWithIndex)  [function, total]
                        | #parseModuleSections2(ModuleDeclOrError, BytesWithIndex)  [function, total]

  rule parseModuleSections(unparsedSectionsResult(S:UnparsedSections, BWI:BytesWithIndex))
      => #parseModuleSections1(parseSections(S), BWI)
  rule parseModuleSections(E:ParseError) => E
  rule #parseModuleSections1(S:Sections, BWI:BytesWithIndex)
      => #parseModuleSections2
          ( addSectionsToModule
              ( S  // Do not reverse, as required by addDefnToModule.
              , moduleAndFunctions
                  ( #module
                      (... types: .Defns
                      , funcs: .Defns
                      , tables: .Defns
                      , mems: .Defns
                      , globals: .Defns
                      , elem: .Defns
                      , data: .Defns
                      , start: .Defns
                      , importDefns: .Defns
                      , exports: .Defns
                      , metadata: #meta(... id: , funcIds: .Map, filename: .String)
                      )
                  , .BinaryDefnFunctionTypes
                  , .BinaryDefnFunctionBodies
                  , .BinaryDefnElements
                  , .BinaryDefnGlobals
                  , .BinaryDefnDatas
                  )
              )
          , BWI
          )
  rule #parseModuleSections1(E:ParseError, _:BytesWithIndex) => E
  rule #parseModuleSections2(M:ModuleDecl, BWI:BytesWithIndex)
      => moduleResult(M, BWI)
  rule #parseModuleSections2(E:ParseError, _:BytesWithIndex) => E

  syntax ModuleDeclOrError ::= addSectionsToModule(Sections, ModuleAndFunctions)  [function, total]
  syntax ModuleDeclOrError ::= #addSectionsToModule(Sections, ModuleAndFunctions)  [function, total]
  rule addSectionsToModule
          ( .Sections
          , moduleAndFunctions
              ( #module(... types: Ds:Defns) #as M:ModuleDecl
              , FT:BinaryDefnFunctionTypes
              , FB:BinaryDefnFunctionBodies
              , E:BinaryDefnElements
              , G:BinaryDefnGlobals
              , D:BinaryDefnDatas
              )
          )
      => addOrderedDefnsOrErrorToModule
          ( M
          , buildFunctionDefns(Ds, FT, FB)
            buildElementDefns(Ds, E)
            buildGlobalDefns(Ds, G)
            buildDataDefns(Ds, D)
            .DefnsOrErrorList
          )
  rule addSectionsToModule(S:Section : Ss:Sections, M:ModuleAndFunctions)
      => #addSectionsToModule(Ss, addSectionToModule(S, M))
  rule #addSectionsToModule(Ss:Sections, M:ModuleAndFunctions)
      => addSectionsToModule(Ss, M)

  syntax ModuleAndFunctions ::= addSectionToModule(Section, ModuleAndFunctions)  [function, total]
  rule addSectionToModule(customSection(_:Bytes), M:ModuleAndFunctions) => M
  rule addSectionToModule(defnsSection(D:BinaryDefns), M:ModuleAndFunctions)
      => addDefnsToModuleAndFunctions(D, M)

  syntax DefnsOrErrorList ::= List{DefnsOrError, ""}

  syntax ModuleDeclOrError ::= addOrderedDefnsOrErrorToModule(ModuleDecl, DefnsOrErrorList)  [function, total]
  rule addOrderedDefnsOrErrorToModule(M:ModuleDecl, .DefnsOrErrorList) => M
  rule addOrderedDefnsOrErrorToModule(M:ModuleDecl, D:Defns Ds:DefnsOrErrorList)
      // We need to reverse the defns because addDefnsToModule adds then in
      // reverse order.
      => addOrderedDefnsOrErrorToModule(addDefnsToModule(reverse(D), M), Ds)
  rule addOrderedDefnsOrErrorToModule(_:ModuleDecl, E:ParseError _:DefnsOrErrorList) => E

  syntax ModuleAndFunctions ::= moduleAndFunctions
                                    ( mod: ModuleDecl
                                    , functionTypes: BinaryDefnFunctionTypes
                                    , functionBodies: BinaryDefnFunctionBodies
                                    , elements: BinaryDefnElements
                                    , globals: BinaryDefnGlobals
                                    , datas: BinaryDefnDatas
                                    )

  syntax ModuleAndFunctions ::= addDefnsToModuleAndFunctions(BinaryDefns, ModuleAndFunctions)  [function, total]
  rule addDefnsToModuleAndFunctions(.BinaryDefns, M:ModuleAndFunctions) => M
  rule addDefnsToModuleAndFunctions
      ( D:Defn Ds:BinaryDefns => Ds
      , moduleAndFunctions(... mod: M:ModuleDecl => addDefnToModule(false, D, M))
      )
  rule addDefnsToModuleAndFunctions
          ( (binaryDefnFunctionType(_TypeIndex:Int) #as FT:BinaryDefnFunctionType) Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... functionTypes: FTs:BinaryDefnFunctionTypes => FT FTs)
          )
  rule addDefnsToModuleAndFunctions
          ( FB:BinaryDefnFunctionBody Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... functionBodies: FBs:BinaryDefnFunctionBodies => FB FBs)
          )
  rule addDefnsToModuleAndFunctions
          ( EB:BinaryDefnElem Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... elements: EBs:BinaryDefnElements => EB EBs)
          )
  rule addDefnsToModuleAndFunctions
          ( G:BinaryDefnGlobal Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... globals: Gs:BinaryDefnGlobals => G Gs)
          )
  rule addDefnsToModuleAndFunctions
          ( G:BinaryDefnData Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... datas: Gs:BinaryDefnDatas => G Gs)
          )

  syntax ModuleDecl ::= addDefnsToModule(Defns, ModuleDecl)  [function, total]
  rule addDefnsToModule(.Defns, M:ModuleDecl) => M
  rule addDefnsToModule
      ( D:Defn Ds:Defns => Ds
      , M:ModuleDecl => addDefnToModule(false, D, M)
      )

  rule addDefnToModule(true, _, M) => M
  // The following add the defn at the top of the existing defns (e.g. T Ts), so
  // addDefnToModule should be called with Defns in reverse order
  // (the last defn should be processed in the first call).
  rule addDefnToModule(false => true, T:TypeDefn, #module(... types: Ts => T Ts))
  rule addDefnToModule(false => true, I:ImportDefn, #module(... importDefns: Is => I Is))
  rule addDefnToModule(false => true, F:FuncDefn, #module(... funcs: Fs => F Fs))
  rule addDefnToModule(false => true, T:TableDefn, #module(... tables: Ts => T Ts))
  rule addDefnToModule(false => true, M:MemoryDefn, #module(... mems: Ms => M Ms))
  rule addDefnToModule(false => true, E:ElemDefn, #module(... elem: Es => E Es))
  rule addDefnToModule(false => true, G:GlobalDefn, #module(... globals: Gs => G Gs))
  rule addDefnToModule(false => true, E:ExportDefn, #module(... exports: Es => E Es))
  rule addDefnToModule(false => true, S:StartDefn, #module(... start: Ss => S Ss))
  rule addDefnToModule(false => true, D:DataDefn, #module(... data: Ds => D Ds))

  // TODO: Merge with #reverseDefns in wasm-text.md
  syntax Defns ::= reverse(Defns)  [function, total]
  rule reverse(D:Defns) => #reverse(D, .Defns)
  syntax Defns ::= #reverse(Defns, Defns) [function, total]
  rule #reverse(.Defns, Ds:Defns) => Ds
  rule #reverse(D:Defn Ds1:Defns, Ds2:Defns) => #reverse(Ds1, D Ds2)

endmodule
```
