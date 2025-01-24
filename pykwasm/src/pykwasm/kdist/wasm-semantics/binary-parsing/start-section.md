Parse the [start section](https://webassembly.github.io/spec/core/binary/modules.html#binary-startsec)

```k
module BINARY-PARSER-START-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX

  syntax SectionResult ::= parseStartSection(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-START-SECTION
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-START-SECTION-SYNTAX
  imports WASM

  syntax SectionResult ::= #parseStartSection(IntResult)  [function, total]

  rule parseStartSection(BWI:BytesWithIndex) => #parseStartSection(parseLeb128UInt(BWI))
  rule #parseStartSection(intResult(I:Int, BWI:BytesWithIndex))
      => sectionResult(defnsSection(#start(I) .BinaryDefns), BWI)
  rule #parseStartSection(E:ParseError) => E

endmodule

```
