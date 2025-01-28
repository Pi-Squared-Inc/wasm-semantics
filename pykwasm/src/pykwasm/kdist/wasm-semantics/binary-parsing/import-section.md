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
      => parseSectionVector(defnImport, Count, .BinaryDefns, BWI)
  rule #parseImportSection(E:ParseError) => E

  syntax DefnKind ::= "defnImport"
  rule parseDefn(defnImport, BWI:BytesWithIndex) => parseDefnImport(BWI)

endmodule
```
