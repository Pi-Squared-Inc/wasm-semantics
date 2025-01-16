Parsing [names](https://webassembly.github.io/spec/core/binary/values.html#binary-name)

```k

module BINARY-PARSER-NAME-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-DATA-COMMON-SYNTAX

  syntax NameResult ::= nameResult(WasmString, BytesWithIndex) | ParseError
  syntax NameResult ::= parseName(BytesWithIndex)  [function, total]
endmodule

module BINARY-PARSER-NAME  [private]
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-NAME-SYNTAX
  imports BOOL

  syntax NameResult ::= #parseName1(IntResult)  [function, total]
                      | #parseName2(String, BytesWithIndex)  [function, total]

  rule parseName(BWI:BytesWithIndex) => #parseName1(parseLeb128UInt(BWI))

  rule #parseName1(intResult(Length:Int, bwi(B:Bytes, Index:Int)))
      // TODO: This should be decoded as an UTF-8 string. However, we do not have
      // a good option when doing concrete execution. The documentation for
      // Bytes2String does not specify an encoding, and decodeBytes is a partial
      // function in a symbolic module.
      => #parseName2
          ( Bytes2String(substrBytes(B, Index, Index +Int Length))
          , bwi(B, Index +Int Length)
          )
      requires 0 <=Int Index andBool Index +Int Length <=Int lengthBytes(B)
  rule #parseName1(intResult(Length:Int, bwi(B:Bytes, Index:Int)))
      => parseError("#parseName1", ListItem(Length) ListItem(Index) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseName1(E:ParseError) => E

  rule #parseName2(S:String, BWI:BytesWithIndex)
      => nameResult
          ( string2WasmString(S)
          , BWI
          )
      requires notBool needsWasmEscaping(S)
  rule #parseName2(S:String, bwi(B:Bytes, Index:Int))
      => parseError("#parseName2", ListItem(S) ListItem(Index) ListItem(lengthBytes(B)) ListItem(B))
      [owise]

endmodule
```
