// Parsing an [import section](https://webassembly.github.io/spec/core/binary/modules.html#binary-importsec).

```k
module BINARY-PARSER-IMPORT-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax SectionResult  ::= parseImportSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-IMPORT-SECTION  [private]
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-IMPORT-SECTION-SYNTAX
  imports BINARY-PARSER-IMPORT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX

  syntax SectionResult  ::= #parseImportSection(IntResult)  [function, total]
  rule parseImportSection(BWI:BytesWithIndex) => #parseImportSection(parseLeb128UInt(BWI))
  rule #parseImportSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseImportSectionVector(Count, .Defns, BWI)
  rule #parseImportSection(E:ParseError) => E

  syntax SectionResult  ::= parseImportSectionVector(remainingCount:Int, Defns, BytesWithIndex)  [function, total]
                          | #parseImportSectionVector(remainingCount:Int, Defns, DefnResult)  [function, total]
  rule parseImportSectionVector(0, D:Defns, BWI:BytesWithIndex) => sectionResult(defnsSection(D), BWI)
  rule parseImportSectionVector(Count:Int, D:Defns, BWI:BytesWithIndex)
      => #parseImportSectionVector(Count, D, parseImport(BWI))
      requires Count >Int 0
  rule parseImportSectionVector(Count:Int, D:Defns, bwi(B:Bytes, I:Int))
      => parseError("parseImportSectionVector", ListItem(Count) ListItem(D) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseImportSectionVector(Count:Int, Ds:Defns, defnResult(D:Defn, BWI:BytesWithIndex))
      => parseImportSectionVector(Count -Int 1, D Ds, BWI)
  rule #parseImportSectionVector(_Count:Int, _:Defns, E:ParseError) => E


endmodule
```
