Splitting a module into [sections](https://webassembly.github.io/spec/core/binary/modules.html#sections).

```k
module BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax Section  ::= customSection(Bytes)
                    | defnsSection(reverseDefns:BinaryDefns)

  syntax DefnKind
  syntax DefnResult ::= parseDefn(DefnKind, BytesWithIndex)  [function, total]

  syntax SectionResult ::= sectionResult(Section, BytesWithIndex) | ParseError
  syntax SectionResult ::= parseSection(UnparsedSection)  [function, total]
  syntax SectionResult  ::= parseSectionVector
                                ( type:DefnKind
                                , remainingCount:Int
                                , BinaryDefns
                                , BytesWithIndex
                                )  [function, total]

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
  imports BINARY-PARSER-CODE-SECTION-SYNTAX
  imports BINARY-PARSER-FUNC-SECTION-SYNTAX
  imports BINARY-PARSER-IMPORT-SECTION-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-TABLE-SECTION-SYNTAX
  imports BINARY-PARSER-TYPE-SECTION-SYNTAX
  imports K-EQUAL-SYNTAX

  rule parseSection(unparsedSection(CUSTOM_SEC, Data:Bytes))
      => sectionResult(customSection(Data), bwi(Data, lengthBytes(Data)))
  rule parseSection(unparsedSection(TYPE_SEC, Data:Bytes))
      => parseTypeSection(bwi(Data, 0))
  rule parseSection(unparsedSection(IMPORT_SEC, Data:Bytes))
      => parseImportSection(bwi(Data, 0))
  rule parseSection(unparsedSection(FUNC_SEC, Data:Bytes))
      => parseFuncSection(bwi(Data, 0))
  rule parseSection(unparsedSection(TABLE_SEC, Data:Bytes))
      => parseTableSection(bwi(Data, 0))
  rule parseSection(unparsedSection(CODE_SEC, Data:Bytes))
      => parseCodeSection(bwi(Data, 0))
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

  syntax SectionResult  ::= #parseSectionVector
                                ( type:DefnKind
                                , remainingCount:Int
                                , BinaryDefns
                                , DefnResult
                                )  [function, total]
  rule parseSectionVector(_:DefnKind, 0, D:BinaryDefns, BWI:BytesWithIndex)
      => sectionResult(defnsSection(D), BWI)
  rule parseSectionVector(T:DefnKind, Count:Int, D:BinaryDefns, BWI:BytesWithIndex)
      => #parseSectionVector(T, Count, D, parseDefn(T, BWI))
      requires Count >Int 0
  rule parseSectionVector(T:DefnKind, Count:Int, D:BinaryDefns, bwi(B:Bytes, I:Int))
      => parseError("parseSectionVector", ListItem(T) ListItem(Count) ListItem(D) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseSectionVector
          ( T:DefnKind
          , RemainingCount:Int
          , Ds:BinaryDefns
          , defnResult(D:BinaryDefn, BWI:BytesWithIndex)
          )
      => parseSectionVector(T, RemainingCount -Int 1, D Ds, BWI)
  rule #parseSectionVector(_:DefnKind, _RemainingCount:Int, _Ds:BinaryDefns, E:ParseError)
      => E



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
