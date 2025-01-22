Parsing a [func section](https://webassembly.github.io/spec/core/binary/modules.html#function-section).

```k
module BINARY-PARSER-FUNC-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax SectionResult  ::= parseFuncSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-FUNC-SECTION  [private]
  imports BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports BINARY-PARSER-FUNC-SECTION-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX

  syntax SectionResult  ::= #parseFuncSection(IntResult)  [function, total]
  rule parseFuncSection(BWI:BytesWithIndex) => #parseFuncSection(parseLeb128UInt(BWI))
  rule #parseFuncSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnFunc, Count, .BinaryDefns, BWI)
  rule #parseFuncSection(E:ParseError) => E

  syntax DefnKind ::= "defnFunc"
  rule parseDefn(defnFunc, BWI:BytesWithIndex) => parseFuncSectionEntry(BWI)

endmodule
```
