// Parsing a [code section](https://webassembly.github.io/spec/core/binary/modules.html#code-section).

```k
module BINARY-PARSER-CODE-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax SectionResult  ::= parseCodeSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-CODE-SECTION  [private]
  imports BINARY-PARSER-CODE-SECTION-SYNTAX
  imports BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX

  syntax SectionResult  ::= #parseCodeSection(IntResult)  [function, total]
  rule parseCodeSection(BWI:BytesWithIndex) => #parseCodeSection(parseLeb128UInt(BWI))
  rule #parseCodeSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnCode, Count, .BinaryDefns, BWI)
  rule #parseCodeSection(E:ParseError) => E

  syntax DefnKind ::= "defnCode"
  rule parseDefn(defnCode, BWI:BytesWithIndex) => parseDefnCode(BWI)
endmodule
```
