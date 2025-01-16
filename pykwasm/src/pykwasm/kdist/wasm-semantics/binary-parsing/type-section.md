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
      => parseTypeSectionVector(Count, .Defns, BWI)
  rule #parseTypeSection(E:ParseError) => E

  syntax SectionResult  ::= parseTypeSectionVector(remainingCount:Int, Defns, BytesWithIndex)  [function, total]
                          | #parseTypeSectionVector(remainingCount:Int, Defns, DefnResult)  [function, total]
  rule parseTypeSectionVector(0, D:Defns, BWI:BytesWithIndex) => sectionResult(defnsSection(D), BWI)
  rule parseTypeSectionVector(Count:Int, D:Defns, BWI:BytesWithIndex)
      => #parseTypeSectionVector(Count, D, parseFuncType(BWI))
      requires Count >Int 0
  rule parseTypeSectionVector(Count:Int, D:Defns, bwi(B:Bytes, I:Int))
      => parseError("parseTypeSectionVector", ListItem(Count) ListItem(D) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseTypeSectionVector(RemainingCount:Int, Ds:Defns, defnResult(D:Defn, BWI:BytesWithIndex))
      => parseTypeSectionVector(RemainingCount -Int 1, D Ds, BWI)
  rule #parseTypeSectionVector(_RemainingCount:Int, _Ds:Defns, E:ParseError)
      => E

endmodule
```
