# Wasm Binary Parser

This file defines a Wasm binary parser based on this
[spec](https://webassembly.github.io/spec/core/binary/index.html).

```k

requires "binary-parsing/base.md"
requires "binary-parsing/binary-defn-convert.md"
requires "binary-parsing/block.md"
requires "binary-parsing/bytes.md"
requires "binary-parsing/code.md"
requires "binary-parsing/constant.md"
requires "binary-parsing/defn.md"
requires "binary-parsing/elem.md"
requires "binary-parsing/export.md"
requires "binary-parsing/expr.md"
requires "binary-parsing/expr-vec.md"
requires "binary-parsing/float.md"
requires "binary-parsing/func-section-entry.md"
requires "binary-parsing/functype.md"
requires "binary-parsing/global.md"
requires "binary-parsing/globaltype.md"
requires "binary-parsing/helpers.md"
requires "binary-parsing/if.md"
requires "binary-parsing/import.md"
requires "binary-parsing/instr.md"
requires "binary-parsing/instr-list.md"
requires "binary-parsing/int.md"
requires "binary-parsing/limits.md"
requires "binary-parsing/locals.md"
requires "binary-parsing/loop.md"
requires "binary-parsing/memarg.md"
requires "binary-parsing/memory.md"
requires "binary-parsing/module.md"
requires "binary-parsing/name.md"
requires "binary-parsing/resulttype.md"
requires "binary-parsing/reftype.md"
requires "binary-parsing/section.md"
requires "binary-parsing/tags.md"
requires "binary-parsing/table.md"
requires "binary-parsing/valtype.md"


module BINARY-PARSER-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax ModuleOrError ::= ModuleDecl | ParseError
  syntax ModuleOrError ::= parseModule(Bytes)  [function, total]
endmodule

module BINARY-PARSER  [private]
  imports BINARY-PARSER-MODULE-SYNTAX

  imports BINARY-PARSER-BINARY-DEFN-CONVERT
  imports BINARY-PARSER-BLOCK
  imports BINARY-PARSER-BYTES
  imports BINARY-PARSER-CODE
  imports BINARY-PARSER-CONSTANT
  imports BINARY-PARSER-ELEM
  imports BINARY-PARSER-EXPORT
  imports BINARY-PARSER-EXPR
  imports BINARY-PARSER-EXPR-VEC
  imports BINARY-PARSER-FLOAT
  imports BINARY-PARSER-FUNC-SECTION-ENTRY
  imports BINARY-PARSER-FUNCTYPE
  imports BINARY-PARSER-GLOBAL
  imports BINARY-PARSER-GLOBALTYPE
  imports BINARY-PARSER-HELPERS
  imports BINARY-PARSER-IF
  imports BINARY-PARSER-IMPORT
  imports BINARY-PARSER-INSTR-LIST
  imports BINARY-PARSER-INSTR
  imports BINARY-PARSER-INT
  imports BINARY-PARSER-LIMITS
  imports BINARY-PARSER-LOCALS
  imports BINARY-PARSER-LOOP
  imports BINARY-PARSER-MEMARG
  imports BINARY-PARSER-MEMORY
  imports BINARY-PARSER-MODULE
  imports BINARY-PARSER-NAME
  imports BINARY-PARSER-RESULTTYPE
  imports BINARY-PARSER-REFTYPE
  imports BINARY-PARSER-SECTION
  imports BINARY-PARSER-SYNTAX
  imports BINARY-PARSER-TABLE
  imports BINARY-PARSER-VALTYPE

  rule parseModule(B:Bytes) => checkAllBytesParsed(parseModule(bwi(B, 0)))

  syntax ModuleOrError ::= checkAllBytesParsed(ModuleResult)  [function, total]
  rule checkAllBytesParsed(moduleResult(M, bwi(B:Bytes, Index:Int))) => M requires Index ==Int lengthBytes(B)
  rule checkAllBytesParsed(E:ParseError) => E

endmodule
```