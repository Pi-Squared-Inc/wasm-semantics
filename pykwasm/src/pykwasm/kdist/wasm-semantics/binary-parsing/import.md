// Parsing an [import](https://webassembly.github.io/spec/core/binary/modules.html#binary-importsec).

```k
module BINARY-PARSER-IMPORT-SYNTAX

  syntax DefnKind ::= "defnImport"

endmodule

module BINARY-PARSER-IMPORT  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-GLOBALTYPE-SYNTAX
  imports BINARY-PARSER-IMPORT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-NAME-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-VALTYPE-SYNTAX
  imports WASM

  rule parseDefn(defnImport, BWI:BytesWithIndex) => parseDefnImport(BWI)

  syntax DefnResult ::= parseDefnImport(BytesWithIndex)  [function, total]
                      | #parseDefnImport1(NameResult)  [function, total]
                      | #parseDefnImport2(WasmString, NameResult)  [function, total]
                      | #parseDefnImport3(WasmString, WasmString, ImportDescResult)  [function, total]
  rule parseDefnImport(BWI:BytesWithIndex) => #parseDefnImport1(parseName(BWI))
  rule #parseDefnImport1(nameResult(Name:WasmString, BWI:BytesWithIndex))
      => #parseDefnImport2(Name, parseName(BWI))
  rule #parseDefnImport1(E:ParseError) => E
  rule #parseDefnImport2(ModuleName:WasmString, nameResult(ObjectName:WasmString, BWI:BytesWithIndex))
      => #parseDefnImport3(ModuleName, ObjectName, parseImportDesc(BWI))
  rule #parseDefnImport2(_, E:ParseError) => E
  rule #parseDefnImport3(ModuleName:WasmString, ObjectName:WasmString, importDescResult(Desc:ImportDesc, BWI:BytesWithIndex))
       => defnResult(#import(ModuleName, ObjectName, Desc), BWI)
  rule #parseDefnImport3(_, _, E:ParseError) => E


  syntax ImportDescResult ::= importDescResult(ImportDesc, BytesWithIndex) | ParseError
  syntax ImportDescResult ::= parseImportDesc(BytesWithIndex)  [function, total]
                            | #parseImportDescFunc(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescTable(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescMem(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescGlobal(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | parseImportDescFunc(IntResult)  [function, total]
                            | parseImportDescTable(ValTypeResult)  [function, total]
                            | #parseImportDescTable1(ValType, LimitsResult)  [function, total]
                            | parseImportDescMem(LimitsResult)  [function, total]
                            | parseImportDescGlobal(GlobalTypeResult)  [function, total]

  rule parseImportDesc(BWI:BytesWithIndex)
      => #parseImportDescFunc(BWI, parseConstant(BWI, IMPORT_FUNC))
  rule #parseImportDescFunc(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescFunc(parseLeb128UInt(BWI))
  rule #parseImportDescFunc(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescTable(BWI, parseConstant(BWI, IMPORT_TBLT))
  rule #parseImportDescTable(_:BytesWithIndex, BWI:BytesWithIndex)
      // TODO: This should use parseRefType in order to properly validate the
      // data, but we are dropping the result for now so we're using the
      // already implemented parseValType.
      => parseImportDescTable(parseValType(BWI))
  rule #parseImportDescTable(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescMem(BWI, parseConstant(BWI, IMPORT_MEMT))
  rule #parseImportDescMem(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescMem(parseLimits(BWI))
  rule #parseImportDescMem(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescGlobal(BWI, parseConstant(BWI, IMPORT_GLBT))
  rule #parseImportDescGlobal(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescGlobal(parseGlobalType(BWI))
  rule #parseImportDescGlobal(_:BytesWithIndex, E:ParseError) => E

  rule parseImportDescFunc(intResult(Value:Int, BWI:BytesWithIndex))
      => importDescResult(#funcDesc(, Value), BWI)
  rule parseImportDescFunc(E:ParseError) => E

  rule parseImportDescTable(valTypeResult(Value:ValType, BWI:BytesWithIndex))
      => #parseImportDescTable1(Value, parseLimits(BWI))
  rule parseImportDescTable(E:ParseError) => E
  // TODO: Do we need RefType for anything?
  rule #parseImportDescTable1(_RefType:ValType, limitsResult(L:Limits, BWI:BytesWithIndex))
      => importDescResult(#tableDesc(, L), BWI)
  rule #parseImportDescTable1(_, E:ParseError) => E

  rule parseImportDescMem(limitsResult(L:Limits, BWI:BytesWithIndex))
      => importDescResult(#memoryDesc(, L), BWI)
  rule parseImportDescMem(E:ParseError) => E

  rule parseImportDescGlobal(globalTypeResult(GT:GlobalType, BWI:BytesWithIndex))
      => importDescResult(#globalDesc(, GT), BWI)
  rule parseImportDescGlobal(E:ParseError) => E

endmodule
```
