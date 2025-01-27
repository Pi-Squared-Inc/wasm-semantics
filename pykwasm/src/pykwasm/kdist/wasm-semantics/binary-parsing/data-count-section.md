Parse the [data count section](https://webassembly.github.io/spec/core/binary/modules.html#binary-datacountsec)

```k
module BINARY-PARSER-DATA-COUNT-SECTION-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-SECTION-SYNTAX

  syntax SectionResult ::= parseDataCountSection(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-DATA-COUNT-SECTION
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-DATA-COUNT-SECTION-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports WASM

  syntax SectionResult ::= #parseDataCountSection(IntResult)  [function, total]

  rule parseDataCountSection(BWI:BytesWithIndex) => #parseDataCountSection(parseLeb128UInt(BWI))
```

It seems that there is no existing constructor for the data count. The
documentation says that is is useful only for validation, so we are ignoring it
for now.

```k
  rule #parseDataCountSection(intResult(_Count:Int, BWI:BytesWithIndex))
      => sectionResult(defnsSection(.BinaryDefns), BWI)
  rule #parseDataCountSection(E:ParseError) => E

endmodule

```
