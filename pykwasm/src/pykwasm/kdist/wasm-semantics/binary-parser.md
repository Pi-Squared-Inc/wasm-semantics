# Wasm Binary Parser

This file defines a Wasm binary parser based on this
[spec](https://webassembly.github.io/spec/core/binary/index.html).

```k

requires "binary-parsing/base.md"
requires "binary-parsing/block.md"
requires "binary-parsing/bytes.md"
requires "binary-parsing/code.md"
requires "binary-parsing/code-section.md"
requires "binary-parsing/constant.md"
requires "binary-parsing/defn.md"
requires "binary-parsing/float.md"
requires "binary-parsing/func-section.md"
requires "binary-parsing/func-section-entry.md"
requires "binary-parsing/functype.md"
requires "binary-parsing/globaltype.md"
requires "binary-parsing/import.md"
requires "binary-parsing/import-section.md"
requires "binary-parsing/instr-list.md"
requires "binary-parsing/instrs.md"
requires "binary-parsing/int.md"
requires "binary-parsing/limits.md"
requires "binary-parsing/locals.md"
requires "binary-parsing/memarg.md"
requires "binary-parsing/module.md"
requires "binary-parsing/name.md"
requires "binary-parsing/resulttype.md"
requires "binary-parsing/section.md"
requires "binary-parsing/tags.md"
requires "binary-parsing/type-section.md"
requires "binary-parsing/valtype.md"


module BINARY-PARSER-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM

  syntax ModuleOrError ::= ModuleDecl | ParseError
  syntax ModuleOrError ::= parseModule(Bytes)  [function, total]
endmodule

module BINARY-PARSER  [private]
  imports BINARY-PARSER-MODULE-SYNTAX

  imports BINARY-PARSER-BLOCK
  imports BINARY-PARSER-BYTES
  imports BINARY-PARSER-CODE
  imports BINARY-PARSER-CODE-SECTION
  imports BINARY-PARSER-CONSTANT
  imports BINARY-PARSER-FLOAT
  imports BINARY-PARSER-FUNC-SECTION
  imports BINARY-PARSER-FUNC-SECTION-ENTRY
  imports BINARY-PARSER-FUNCTYPE
  imports BINARY-PARSER-GLOBALTYPE
  imports BINARY-PARSER-IMPORT
  imports BINARY-PARSER-IMPORT-SECTION
  imports BINARY-PARSER-INSTR-LIST
  imports BINARY-PARSER-INSTRS
  imports BINARY-PARSER-INT
  imports BINARY-PARSER-LIMITS
  imports BINARY-PARSER-LOCALS
  imports BINARY-PARSER-MEMARG
  imports BINARY-PARSER-MODULE
  imports BINARY-PARSER-NAME
  imports BINARY-PARSER-RESULTTYPE
  imports BINARY-PARSER-SECTION
  imports BINARY-PARSER-SYNTAX
  imports BINARY-PARSER-TYPE-SECTION
  imports BINARY-PARSER-VALTYPE

  rule parseModule(B:Bytes) => checkAllBytesParsed(parseModule(bwi(B, 0)))

  syntax ModuleOrError ::= checkAllBytesParsed(ModuleResult)  [function, total]
  rule checkAllBytesParsed(moduleResult(M, bwi(B:Bytes, Index:Int))) => M requires Index ==Int lengthBytes(B)
  rule checkAllBytesParsed(E:ParseError) => E

endmodule
```