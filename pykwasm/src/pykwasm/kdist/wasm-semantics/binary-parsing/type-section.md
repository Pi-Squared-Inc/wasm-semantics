Parsing a [type section](https://webassembly.github.io/spec/core/binary/modules.html#binary-typesec).

```k
module BINARY-PARSER-TYPE-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax SectionResult  ::= parseTypeSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-TYPE-SECTION  [private]
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-FUNCTYPE-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TYPE-SECTION-SYNTAX

  syntax SectionResult  ::= #parseTypeSection(IntResult)  [function, total]
  rule parseTypeSection(BWI:BytesWithIndex) => #parseTypeSection(parseLeb128UInt(BWI))
  rule #parseTypeSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnType, Count, .BinaryDefns, BWI)
  rule #parseTypeSection(E:ParseError) => E

  syntax DefnKind ::= "defnType"
  rule parseDefn(defnType, BWI:BytesWithIndex) => parseDefnType(BWI)

endmodule
```
