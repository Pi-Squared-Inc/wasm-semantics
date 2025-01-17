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
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-MODULE-SYNTAX
  imports BINARY-PARSER-MODULE-TEST-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TAGS

  rule parseModule(BWI:BytesWithIndex)
      => parseModuleSections(reverseSections(splitSections(parseConstant(parseConstant(BWI, MAGIC), VERSION))))

  syntax ModuleResult  ::= parseModuleSections(UnparsedSectionsResult)  [function, total]
                              | #parseModuleSections(ParsedSectionsResult, BytesWithIndex)  [function, total]

  rule parseModuleSections(unparsedSectionsResult(S:UnparsedSections, BWI:BytesWithIndex))
      => #parseModuleSections(parseSections(S), BWI)
  rule parseModuleSections(E:ParseError) => E
  rule #parseModuleSections(S:Sections, BWI:BytesWithIndex)
      => moduleResult
          ( addSectionsToModule
              ( S  // Do not reverse, as required by addDefnToModule.
              , #module
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
              ), BWI)
  rule #parseModuleSections(E:ParseError, _:BytesWithIndex) => E

  syntax ModuleDecl ::= addSectionsToModule(Sections, ModuleDecl)  [function, total]
  rule addSectionsToModule(.Sections, M:ModuleDecl) => M
  rule addSectionsToModule(S:Section : Ss:Sections, M:ModuleDecl)
      => addSectionsToModule(Ss, addSectionToModule(S, M))
  syntax ModuleDecl ::= addSectionToModule(Section, ModuleDecl)  [function, total]
  rule addSectionToModule(customSection(_:Bytes), M:ModuleDecl) => M
  rule addSectionToModule(defnsSection(D:Defns), M:ModuleDecl) => addDefnsToModule(D, M)
  syntax ModuleDecl ::= addDefnsToModule(Defns, ModuleDecl)  [function, total]
  rule addDefnsToModule(.Defns, M:ModuleDecl) => M
  rule addDefnsToModule(D:Defn Ds:Defns, M:ModuleDecl)
      => addDefnsToModule(Ds, addDefnToModule(false, D, M))

  rule addDefnToModule(true, _, M) => M
  // The following add the defn at the top of the existing defns (e.g. T Ts), so
  // addDefnToModule should be called with Defns in reverse order
  // (the last defn should be processed in the first call).
  rule addDefnToModule(false => true, T:TypeDefn, #module(... types: Ts => T Ts))
  rule addDefnToModule(false => true, I:ImportDefn, #module(... importDefns: Is => I Is))

endmodule
```
