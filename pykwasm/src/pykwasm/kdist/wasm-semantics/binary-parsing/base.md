```k

module BINARY-PARSER-BASE-SYNTAX
  imports BYTES
  imports INT
  imports LIST
  imports STRING

  syntax BytesWithIndex ::= bwi(Bytes, Int)
  syntax ParseError ::= parseError(String, List)

  syntax BytesWithIndexOrError ::= BytesWithIndex | ParseError

endmodule

```