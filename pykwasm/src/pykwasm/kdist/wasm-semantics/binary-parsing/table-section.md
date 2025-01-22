Parsing a [table section](https://webassembly.github.io/spec/core/binary/modules.html#binary-tablesec).

```k
module BINARY-PARSER-TABLE-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax SectionResult  ::= parseTableSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-TABLE-SECTION  [private]
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TABLE-SECTION-SYNTAX
  imports BINARY-PARSER-TABLE-SYNTAX

  syntax SectionResult  ::= #parseTableSection(IntResult)  [function, total]
  rule parseTableSection(BWI:BytesWithIndex) => #parseTableSection(parseLeb128UInt(BWI))
  rule #parseTableSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnTable, Count, .BinaryDefns, BWI)
  rule #parseTableSection(E:ParseError) => E

  syntax DefnKind ::= "defnTable"
  rule parseDefn(defnTable, BWI:BytesWithIndex) => parseDefnTable(BWI)

endmodule
```
