Splitting a module into [sections](https://webassembly.github.io/spec/core/binary/modules.html#sections).

```k
module BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax Section  ::= customSection(Bytes)
                    | defnsSection(reverseDefns:BinaryDefns)

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
  imports BINARY-PARSER-CODE-SYNTAX
  imports BINARY-PARSER-ELEM-SYNTAX
  imports BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports BINARY-PARSER-IMPORT-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-MEMORY-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX
  imports BINARY-PARSER-TAGS
  imports BINARY-PARSER-TABLE-SYNTAX
  imports BINARY-PARSER-FUNCTYPE-SYNTAX
  imports K-EQUAL-SYNTAX

  rule parseSection(unparsedSection(CUSTOM_SEC, Data:Bytes))
      => sectionResult(customSection(Data), bwi(Data, lengthBytes(Data)))
  rule parseSection(unparsedSection(TYPE_SEC, Data:Bytes))
      => #parseSection1(defnType, bwi(Data, 0))
  rule parseSection(unparsedSection(IMPORT_SEC, Data:Bytes))
      => #parseSection1(defnImport, bwi(Data, 0))
  rule parseSection(unparsedSection(FUNC_SEC, Data:Bytes))
      => #parseSection1(defnFunc, bwi(Data, 0))
  rule parseSection(unparsedSection(TABLE_SEC, Data:Bytes))
      => #parseSection1(defnTable, bwi(Data, 0))
  rule parseSection(unparsedSection(MEMORY_SEC, Data:Bytes))
      => #parseSection1(defnMemory, bwi(Data, 0))
  rule parseSection(unparsedSection(ELT_SEC, Data:Bytes))
      => #parseSection1(defnElem, bwi(Data, 0))
  rule parseSection(unparsedSection(CODE_SEC, Data:Bytes))
      => #parseSection1(defnCode, bwi(Data, 0))
  rule parseSection(A) => parseError("parseSection", ListItem(A))
      [owise]

  syntax SectionResult  ::= #parseSection1(DefnKind, BytesWithIndex)  [function, total]
                          | #parseSection2(DefnKind, IntResult)  [function, total]
  rule #parseSection1(D:DefnKind, BWI:BytesWithIndex) => #parseSection2(D, parseLeb128UInt(BWI))
  rule #parseSection2(D:DefnKind, intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(D, Count, .BinaryDefns, BWI)
  rule #parseSection2(_:DefnKind, E:ParseError) => E

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
