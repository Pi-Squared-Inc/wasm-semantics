Splitting a module into [sections](https://webassembly.github.io/spec/core/binary/modules.html#sections).

```k
module BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax Section  ::= customSection(Bytes)
                    | defnsSection(reverseDefns:Defns)

  syntax SectionResult ::= sectionResult(Section, BytesWithIndex) | ParseError
  syntax SectionResult ::= parseSection(UnparsedSection)  [function, total]

  syntax Sections ::= List{Section, ":"}
  syntax ParsedSectionsResult ::= Sections | ParseError
  syntax ParsedSectionsResult ::= parseSections(UnparsedSections)  [function, total]

  syntax UnparsedSection ::= unparsedSection(sectionId:Int, sectionData:Bytes)

  syntax UnparsedSections ::= List{UnparsedSection, ":"}
  syntax UnparsedSectionsResult ::= unparsedSectionsResult(UnparsedSections, BytesWithIndex) | ParseError
  syntax UnparsedSectionsResult ::= splitSections(BytesWithIndexOrError)  [function, total]

  syntax UnparsedSectionsResult ::= reverseSections(UnparsedSectionsResult)  [function, total]
endmodule

module BINARY-PARSER-SECTION  [private]
  imports BOOL
  imports BINARY-PARSER-IMPORT-SECTION-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-TYPE-SECTION-SYNTAX
  imports K-EQUAL-SYNTAX

  rule parseSection(unparsedSection(CUSTOM_SEC, Data:Bytes))
      => sectionResult(customSection(Data), bwi(Data, lengthBytes(Data)))
  rule parseSection(unparsedSection(TYPE_SEC, Data:Bytes))
      => parseTypeSection(bwi(Data, 0))
  rule parseSection(unparsedSection(IMPORT_SEC, Data:Bytes))
      => parseImportSection(bwi(Data, 0))
  rule parseSection(A) => parseError("parseSection", ListItem(A))
      [owise]


  syntax ParsedSectionsResult ::= #parseSections(SectionResult, ParsedSectionsResult)  [function, total]
  rule parseSections(.UnparsedSections) => .Sections
  rule parseSections(S:UnparsedSection : Ss:UnparsedSections)
      => #parseSections(parseSection(S), parseSections(Ss))
  rule #parseSections(sectionResult(S:Section, bwi(B:Bytes, I:Int)), Ss:Sections)
      => S : Ss
      requires I ==K lengthBytes(B)
  rule #parseSections(E:ParseError, _) => E
  rule #parseSections(_, E:ParseError) => E
    [owise]


  syntax UnparsedSectionResult ::= unparsedSectionResult(UnparsedSection, BytesWithIndex) | ParseError
  syntax UnparsedSectionResult  ::= splitSection(BytesWithIndex) [function, total]

  syntax UnparsedSectionResult  ::= #splitSection(sectionId:Int, IntResult) [function, total]

  rule splitSection(bwi(Buffer:Bytes, Index:Int))
      => #splitSection(Buffer[Index], parseLeb128UInt(bwi(Buffer, Index +Int 1)))
      requires Index <Int lengthBytes(Buffer)

  rule #splitSection(SectionId, intResult(SectionLength:Int, bwi(Buffer:Bytes, Index:Int)))
      => unparsedSectionResult
          ( unparsedSection(SectionId, substrBytes(Buffer, Index, Index +Int SectionLength))
          , bwi(Buffer, Index +Int SectionLength)
          )
      requires 0 <=Int Index andBool Index +Int SectionLength <=Int lengthBytes(Buffer)
  rule #splitSection(SectionId:Int, intResult(SectionLength:Int, bwi(Buffer:Bytes, Index:Int)))
      => parseError("splitSection", ListItem(SectionId) ListItem(SectionLength) ListItem(Index) ListItem(lengthBytes(Buffer)) ListItem(Buffer))
      [owise]
  rule #splitSection(_SectionId:Int, E:ParseError) => E


  syntax UnparsedSections ::= reverse(UnparsedSections)  [function, total]
                            | #reverse(UnparsedSections, UnparsedSections)  [function, total]
  rule reverse(S:UnparsedSections) => #reverse(S, .UnparsedSections)
  rule #reverse(.UnparsedSections, S:UnparsedSections) => S
  rule #reverse(S:UnparsedSection : Ss1:UnparsedSections, Ss2:UnparsedSections) => #reverse(Ss1, S: Ss2)

  rule reverseSections(unparsedSectionsResult(S:UnparsedSections, BWI:BytesWithIndex))
      => unparsedSectionsResult(reverse(S), BWI)
  rule reverseSections(E:ParseError) => E

  syntax UnparsedSectionsResult ::= #splitSections(UnparsedSectionResult)  [function, total]
                                  | concatOrError(UnparsedSection, UnparsedSectionsResult)  [function, total]

  rule splitSections(bwi(B:Bytes, Index:Int))
      => unparsedSectionsResult(.UnparsedSections, bwi(B:Bytes, Index:Int))
      requires Index ==K lengthBytes(B)
  rule splitSections(BWI:BytesWithIndex)
      => #splitSections(splitSection(BWI))
      [owise]
  rule splitSections(E:ParseError) => E

  rule #splitSections(unparsedSectionResult(S:UnparsedSection, BWI:BytesWithIndex))
      => concatOrError(S, splitSections(BWI))
  rule #splitSections(E:ParseError) => E

  rule concatOrError(S:UnparsedSection, unparsedSectionsResult(Ss:UnparsedSections, BWI:BytesWithIndex))
      => unparsedSectionsResult(S : Ss, BWI)
  rule concatOrError(_:UnparsedSection, E:ParseError) => E

endmodule
```
