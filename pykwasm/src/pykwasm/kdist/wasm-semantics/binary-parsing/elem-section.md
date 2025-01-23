Parsing an [element section](https://webassembly.github.io/spec/core/binary/modules.html#binary-elemsec).

```k
module BINARY-PARSER-ELEM-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax SectionResult  ::= parseElemSection(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-ELEM-SECTION  [private]
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-ELEM-SECTION-SYNTAX
  imports BINARY-PARSER-ELEM-SYNTAX

  syntax SectionResult  ::= #parseElemSection(IntResult)  [function, total]
  rule parseElemSection(BWI:BytesWithIndex) => #parseElemSection(parseLeb128UInt(BWI))
  rule #parseElemSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnElem, Count, .BinaryDefns, BWI)
  rule #parseElemSection(E:ParseError) => E

  syntax DefnKind ::= "defnElem"
  rule parseDefn(defnElem, BWI:BytesWithIndex) => parseDefnElem(BWI)

endmodule
```
