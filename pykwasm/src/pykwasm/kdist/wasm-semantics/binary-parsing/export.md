// Parsing an [export section entry](https://webassembly.github.io/spec/core/binary/modules.html#export-section).

```k
module BINARY-PARSER-EXPORT-SYNTAX
  imports BINARY-PARSER-INSTR-LIST-SYNTAX
  imports WASM

  syntax DefnKind ::= "defnExport"

endmodule

module BINARY-PARSER-EXPORT  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-EXPORT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-NAME-SYNTAX
  imports BINARY-PARSER-TAGS
  imports WASM

  rule parseDefn(defnExport, BWI:BytesWithIndex) => parseDefnExport(BWI)

  syntax DefnResult ::= parseDefnExport(BytesWithIndex)  [function, total]
                      | #parseDefnExport1(NameResult)  [function, total]
                      | #parseDefnExport2(WasmString, ExportDescResult)  [function, total]
  rule parseDefnExport(BWI:BytesWithIndex) => #parseDefnExport1(parseName(BWI))
  rule #parseDefnExport1(nameResult(N:WasmString, BWI:BytesWithIndex))
      => #parseDefnExport2(N, parseExportDesc(BWI))
  rule #parseDefnExport1(E:ParseError) => E

```

  This follows the code in wasm-text.md (search for #export).

  **TODO**: Does it make sense to mix the IDs, as the current code does?
  Should the `<exports>` cell actually contain (AllocatedKind, Int) tuples?
  Right now, if module A calls module B, B trusts A to use its exports with
  the proper type.

```k

  rule #parseDefnExport2(N:WasmString, exportDescResult(_:AllocatedKind Index:Int, BWI:BytesWithIndex))
      => defnResult(#export(N, Index), BWI)
  rule #parseDefnExport2(N:WasmString, exportDescResult(V:Externval, BWI:BytesWithIndex))
      => parseError("#parseDefnExport2: unimplemented", ListItem(N) ListItem(V) ListItem(BWI))
      [owise]
  rule #parseDefnExport2(_:WasmString, E:ParseError) => E


  syntax ExportDescResult ::= exportDescResult(Externval, BytesWithIndex) | ParseError

  syntax ExportDescResult ::= parseExportDesc(BytesWithIndex)  [function, total]
                            | #parseExportDesc1(IntResult)  [function, total]
                            | #parseExportDesc2(AllocatedKind, IntResult)  [function, total]
  rule parseExportDesc(BWI:BytesWithIndex) => #parseExportDesc1(parseByteAsInt(BWI))

  rule #parseExportDesc1(intResult(EXPORT_FUNC, BWI:BytesWithIndex))
      => #parseExportDesc2(func, parseLeb128UInt(BWI))
  rule #parseExportDesc1(intResult(EXPORT_TBLT, BWI:BytesWithIndex))
      => #parseExportDesc2(table, parseLeb128UInt(BWI))
  rule #parseExportDesc1(intResult(EXPORT_MEMT, BWI:BytesWithIndex))
      => #parseExportDesc2(memory, parseLeb128UInt(BWI))
  rule #parseExportDesc1(intResult(EXPORT_GLBT, BWI:BytesWithIndex))
      => #parseExportDesc2(global, parseLeb128UInt(BWI))
  rule #parseExportDesc1(intResult(I:Int, BWI:BytesWithIndex))
      => parseError("#parseExportDesc1", ListItem(I) ListItem(BWI))
      [owise]
  rule #parseExportDesc1(E:ParseError) => E

  rule #parseExportDesc2(A:AllocatedKind, intResult(Index:Int, BWI:BytesWithIndex))
      => exportDescResult(A Index, BWI)
  rule #parseExportDesc2(_:AllocatedKind, E:ParseError) => E

endmodule
```
