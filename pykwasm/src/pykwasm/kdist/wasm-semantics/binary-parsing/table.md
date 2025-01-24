Parsing a [table](https://webassembly.github.io/spec/core/binary/modules.html#binary-tablesec).

```k
module BINARY-PARSER-TABLE-SYNTAX

  syntax DefnKind ::= "defnTable"

endmodule

module BINARY-PARSER-TABLE  [private]
  imports BINARY-PARSER-BASE-SYNTAX
  imports BINARY-PARSER-DEFN-SYNTAX
  imports BINARY-PARSER-LIMITS-SYNTAX
  imports BINARY-PARSER-TABLE-SYNTAX
  imports BINARY-PARSER-VALTYPE-SYNTAX

  rule parseDefn(defnTable, BWI:BytesWithIndex) => parseDefnTable(BWI)

  syntax DefnResult ::= parseDefnTable(BytesWithIndex)  [function, total]
                      | #parseDefnTable1(ValTypeResult)  [function, total]
                      | #parseDefnTable2(RefValType, LimitsResult)  [function, total]
  rule parseDefnTable(BWI:BytesWithIndex) => #parseDefnTable1(parseValType(BWI))
  rule #parseDefnTable1(valTypeResult(T:RefValType, BWI:BytesWithIndex))
      => #parseDefnTable2(T, parseLimits(BWI))
  rule #parseDefnTable1(valTypeResult(T:ValType, BWI:BytesWithIndex))
      => parseError("#parseDefnTable1", ListItem(T) ListItem(BWI))
      [owise]
  rule #parseDefnTable1(E:ParseError) => E
  rule #parseDefnTable2(T:RefValType, limitsResult(L:Limits, BWI:BytesWithIndex))
      => defnResult(#table(L, T, ), BWI)
  rule #parseDefnTable2(_, E:ParseError) => E

endmodule
```
