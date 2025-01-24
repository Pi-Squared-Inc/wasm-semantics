Parsing a [function type idx](https://webassembly.github.io/spec/core/binary/types.html#binary-functype).

```k
module BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX

  syntax DefnKind ::= "defnFunc"

  syntax BinaryDefnFunctionTypes ::= List{BinaryDefnFunctionType, ""}

  syntax BinaryDefnFunctionType ::= binaryDefnFunctionType(typeIndex: Int)
  syntax BinaryDefn ::= BinaryDefnFunctionType

endmodule

module BINARY-PARSER-FUNC-SECTION-ENTRY  [private]
  imports BINARY-PARSER-FUNC-SECTION-ENTRY-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX

  rule parseDefn(defnFunc, BWI:BytesWithIndex) => parseFuncSectionEntry(BWI)

  syntax DefnResult ::= parseFuncSectionEntry(BytesWithIndex)  [function, total]
                      | #parseFuncSectionEntry(IntResult)  [function, total]

  rule parseFuncSectionEntry(BWI:BytesWithIndex)
      => #parseFuncSectionEntry(parseLeb128UInt(BWI))
  rule #parseFuncSectionEntry(intResult(TypeIndex:Int, BWI:BytesWithIndex))
      => defnResult(binaryDefnFunctionType(TypeIndex), BWI)
  rule #parseFuncSectionEntry(E:ParseError) => E

endmodule
```
