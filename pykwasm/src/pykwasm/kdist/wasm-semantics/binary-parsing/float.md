Parsing a [float](https://webassembly.github.io/spec/core/binary/values.html#floating-point).

```k
module BINARY-PARSER-FLOAT-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX

  syntax FloatResult ::= floatResult(Float, BytesWithIndex) | ParseError

  syntax FloatResult  ::= parseFloat64(BytesWithIndex)  [function, total]
  syntax FloatResult  ::= parseFloat32(BytesWithIndex)  [function, total]

endmodule

module BINARY-PARSER-FLOAT  [private]
  imports BINARY-PARSER-BYTES-SYNTAX
  imports BINARY-PARSER-FLOAT-SYNTAX

  syntax FloatResult  ::= #parseFloat64(BytesResult)  [function, total]
  rule parseFloat64(BWI:BytesWithIndex) => #parseFloat64(parseBytes(BWI, 8))
  rule #parseFloat64(bytesResult(Bytes:Bytes, BWI:BytesWithIndex))
      => parseError("#parseFloat64: bytesToFloat is not implemented", ListItem(Bytes) ListItem(BWI))  // float(bytesToFloat(Bytes), BWI)
  rule #parseFloat64(E:ParseError) => E

  syntax FloatResult  ::= #parseFloat32(BytesResult)  [function, total]
  rule parseFloat32(BWI:BytesWithIndex) => #parseFloat32(parseBytes(BWI, 4))
  rule #parseFloat32(bytesResult(Bytes:Bytes, BWI:BytesWithIndex))
      => parseError("#parseFloat32: bytesToFloat is not implemented", ListItem(Bytes) ListItem(BWI))  // float(bytesToFloat(Bytes), BWI)
  rule #parseFloat32(E:ParseError) => E

  // syntax Float ::= bytesToFloat(Bytes) [function, total]
  // TODO: implement.

endmodule
```
