# Wasm Binary Parser

This file defines a Wasm binary parser.
To begin, we define constant macros which drive the parser process.

```k
module BINARY_PARSER_DATA
  imports BYTES
```

## Wasm Metadata Parser Tags

Every Wasm module starts with a 4-byte header and a 4-byte version.

```k
  syntax Bytes ::= MAGIC   [macro] rule MAGIC   => b"x00x61x73x6D"
                 | VERSION [macro] rule VERSION => b"x01x00x00x00"
```

After that, a Wasm module is an ordered list of sections, each prefixed with a section id.

```k
                 | CUSTOM_SEC [macro] rule CUSTOM_SEC => b"x00"
                 | TYPE_SEC   [macro] rule TYPE_SEC   => b"x01"
                 | IMPORT_SEC [macro] rule IMPORT_SEC => b"x02"
                 | FUNC_SEC   [macro] rule FUNC_SEC   => b"x03"
                 | TABLE_SEC  [macro] rule TABLE_SEC  => b"x04"
                 | MEMORY_SEC [macro] rule MEMORY_SEC => b"x05"
                 | GLOBAL_SEC [macro] rule GLOBAL_SEC => b"x06"
                 | EXPORT_SEC [macro] rule EXPORT_SEC => b"x07"
                 | START_SEC  [macro] rule START_SEC  => b"x08"
                 | ELT_SEC    [macro] rule ELT_SEC    => b"x09"
                 | CODE_SEC   [macro] rule CODE_SEC   => b"x0a"
                 | DAT_SEC    [macro] rule DAT_SEC    => b"x0b"
                 | CNT_SEC    [macro] rule CNT_SEC    => b"x0c"
```

In the import/export sections, different kinds of imports/exports are tagged.

```k
                 | IMPORT_FUNC [macro] rule IMPORT_FUNC => b"x00"
                 | IMPORT_TBLT [macro] rule IMPORT_TBLT => b"x01"
                 | IMPORT_MEMT [macro] rule IMPORT_MEMT => b"x02"
                 | IMPORT_GLBT [macro] rule IMPORT_GLBT => b"x03"
                 | EXPORT_FUNC [macro] rule EXPORT_FUNC => b"x00"
                 | EXPORT_TBLT [macro] rule EXPORT_TBLT => b"x01"
                 | EXPORT_MEMT [macro] rule EXPORT_MEMT => b"x02"
                 | EXPORT_GLBT [macro] rule EXPORT_GLBT => b"x03"
```

_Element_ sections have various possible formats which are stored in a 3-bit code.
The possible code words are explained in the table below:

Bit # | Constraint | 0 State         | 1 State              |
----- | ---------- | --------------- | -------------------- |
0     | None       | active          | passive/declarative  |
1     | Bit[0]=0   | has table index | zero table index     |
1     | Bit[0]=1   | passive         | declarative          |
2     | None       | elts by ref     | elts by value        |

```k
                 | ELTS_ACTIVE_ZERO_BY_REF [macro] // 000
                 | ELTS_PASSIVE_BY_REF     [macro] // 001
                 | ELTS_ACTIVE_IDX_BY_REF  [macro] // 010
                 | ELTS_DECL_BY_REF        [macro] // 011
                 | ELTS_ACTIVE_ZERO_BY_VAL [macro] // 100
                 | ELTS_PASSIVE_BY_VAL     [macro] // 101
                 | ELTS_ACTIVE_IDX_BY_VAL  [macro] // 110
                 | ELTS_DECL_BY_VAL        [macro] // 110

  rule ELTS_ACTIVE_ZERO_BY_REF => b"x00"
  rule ELTS_PASSIVE_BY_REF     => b"x01"
  rule ELTS_ACTIVE_IDX_BY_REF  => b"x02"
  rule ELTS_DECL_BY_REF        => b"x03"
  rule ELTS_ACTIVE_ZERO_BY_VAL => b"x04"
  rule ELTS_PASSIVE_BY_VAL     => b"x05"
  rule ELTS_ACTIVE_IDX_BY_VAL  => b"x06"
  rule ELTS_DECL_BY_VAL        => b"x07"
```

The special _element kind_ constant is used to describe possible element kinds.
Currently, only one element kind is supported.

```k
                 | ELT_KIND [macro] rule ELT_KIND => b"x00"
```

_Data_ sections are tagged based on their kind.

```k
                 | DATA_ACTIVE_ZERO [macro] rule DATA_ACTIVE_ZERO  => b"x00"
                 | DATA_PASSIVE     [macro] rule DATA_PASSIVE_ZERO => b"x01"
                 | DATA_ACTIVE_IDX  [macro] rule DATA_ACTIVE_IDX   => b"x02"
```

Each value _type_ is tagged by a unique integer.
There are two special types: functions and empty types.
These have special use requirements as we will see later.

```k
                 | TYPE_I32     [macro] rule TYPE_I32     => b"x7F"
                 | TYPE_I64     [macro] rule TYPE_I64     => b"x7E"
                 | TYPE_F32     [macro] rule TYPE_F32     => b"x7D"
                 | TYPE_F64     [macro] rule TYPE_F64     => b"x7C"
                 | TYPE_VEC     [macro] rule TYPE_VEC     => b"x7B"
                 | TYPE_FUN_REF [macro] rule TYPE_FUN_REF => b"x70"
                 | TYPE_EXT_REF [macro] rule TYPE_EXT_REF => b"x64"
                 | TYPE_FUN     [macro] rule TYPE_FUN     => b"x60"
                 | TYPE_EMPTY   [macro] rule TYPE_EMPTY   => b"x40"
```

_Limits_ are used to encode the minimum size of memories and tables;
a separate form that also specifies a maximum size is available.

```k
                 | LIMITS     [macro] rule LIMITS     => b"x00"
                 | LIMITS_MAX [macro] rule LIMITS_MAX => b"x01"
```

_Globals_ may be declared as mutable or immutable.

```k
                 | GLOBAL_CNST [macro] rule GLOBAL_CNST => b"x00"
                 | GLOBAL_VAR  [macro] rule GLOBAL_VAR  => b"x01"
```

## Wasm Instruction Parser Tags

Wasm _control instructions_ are encoded with the follow tags.
Note that `ELSE` instructions must appear in conjunction with `IF` instructions.

```k
  syntax Bytes ::= UNREACHABLE   [macro] rule UNREACHABLE   => b"x00"
                 | NOP           [macro] rule NOP           => b"x01"
                 | BLOCK         [macro] rule BLOCK         => b"x02"
                 | LOOP          [macro] rule LOOP          => b"x03"
                 | IF            [macro] rule IF            => b"x04"
                 | ELSE          [macro] rule ELSE          => b"x05"
                 | BR            [macro] rule BR            => b"x0C"
                 | BR_IF         [macro] rule BR_IF         => b"x0D"
                 | BR_TABLE      [macro] rule BR_TABLE      => b"x0E"
                 | RETURN        [macro] rule RETURN        => b"x0F"
                 | CALL          [macro] rule CALL          => b"x10"
                 | CALL_INDIRECT [macro] rule CALL_INDIRECT => b"x11"
```

_Reference instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= REF_NULL   [macro] rule REF_NULL   => b"xD0"
                 | REF_ISNULL [macro] rule REF_ISNULL => b"xD1"
                 | REF_FUNC   [macro] rule REF_FUNC   => b"xD2"
```

_Variable instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= LOCAL_GET  [macro] rule LOCAL_GET  => b"x20"
                 | LOCAL_SET  [macro] rule LOCAL_SET  => b"x21"
                 | LOCAL_TEE  [macro] rule LOCAL_TEE  => b"x22"
                 | GLOBAL_GET [macro] rule GLOBAL_GET => b"x23"
                 | GLOBAL_SET [macro] rule GLOBAL_SET => b"x24"
```

_Table instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= TABLE_GET  [macro] rule TABLE_GET  => b"x25"
                 | TABLE_SET  [macro] rule TABLE_SET  => b"x26"
                 | TABLE_INIT [macro] rule TABLE_INIT => b"xFCx0C"
                 | ELEM_DROP  [macro] rule ELEM_DROP  => b"xFCx0D"
                 | TABLE_COPY [macro] rule TABLE_COPY => b"xFCx0E"
                 | TABLE_GROW [macro] rule TABLE_GROW => b"xFCx0F"
                 | TABLE_SIZE [macro] rule TABLE_SIZE => b"xFCx10"
                 | TABLE_FILL [macro] rule TABLE_FILL => b"xFCx11"
```

_Memory instructions_ are encoded with the following tags:

```k
                 | I32_LOAD      [macro] rule I32_LOAD      => b"x28"
                 | I64_LOAD      [macro] rule I64_LOAD      => b"x29"
                 | F32_LOAD      [macro] rule F32_LOAD      => b"x2A"
                 | F64_LOAD      [macro] rule F64_LOAD      => b"x2B"
                 | I32_LOAD_8_S  [macro] rule I32_LOAD_8_S  => b"x2C"
                 | I32_LOAD_8_U  [macro] rule I32_LOAD_8_U  => b"x2D"
                 | I32_LOAD_16_S [macro] rule I32_LOAD_16_S => b"x2E"
                 | I32_LOAD_16_U [macro] rule I32_LOAD_16_U => b"x2F"
                 | I64_LOAD_8_S  [macro] rule I64_LOAD_8_S  => b"x30"
                 | I64_LOAD_8_U  [macro] rule I64_LOAD_8_U  => b"x31"
                 | I64_LOAD_16_S [macro] rule I64_LOAD_16_S => b"x32"
                 | I64_LOAD_16_U [macro] rule I64_LOAD_16_U => b"x33"
                 | I64_LOAD_32_S [macro] rule I64_LOAD_32_S => b"x34"
                 | I64_LOAD_32_U [macro] rule I64_LOAD_32_U => b"x35"
                 | I32_STORE     [macro] rule I32_STORE     => b"x36"
                 | I64_STORE     [macro] rule I64_STORE     => b"x37"
                 | F32_STORE     [macro] rule F32_STORE     => b"x38"
                 | F64_STORE     [macro] rule F64_STORE     => b"x39"
                 | I32_STORE_8   [macro] rule I32_STORE_8   => b"x3A"
                 | I32_STORE_16  [macro] rule I32_STORE_16  => b"x3B"
                 | I64_STORE_8   [macro] rule I64_STORE_8   => b"x3C"
                 | I64_STORE_16  [macro] rule I64_STORE_16  => b"x3D"
                 | I64_STORE_32  [macro] rule I64_STORE_32  => b"x3E"
                 | MEM_SIZE      [macro] rule MEM_SIZE      => b"x3F"
                 | MEM_GROW      [macro] rule MEM_GROW      => b"x40"
                 | MEM_INIT      [macro] rule MEM_INIT      => b"xFCx08"
                 | DATA_DROP     [macro] rule DATA_DROP     => b"xFCx09"
                 | MEM_COPY      [macro] rule MEM_COPY      => b"xFCx0A"
                 | MEM_FILL      [macro] rule MEM_FILL      => b"xFCx0B"
```

_Numeric instructions_ have the following tags:

```k
                 | I32_CONST           [macro] rule I32_CONST => b"x41"
                 | I64_CONST           [macro] rule I64_CONST => b"x42"
                 | F32_CONST           [macro] rule F32_CONST => b"x43"
                 | F64_CONST           [macro] rule F64_CONST => b"x44"

                 | I32_EQZ             [macro] rule I32_EQZ  => b"x45"
                 | I32_EQ              [macro] rule I32_EQ   => b"x46"
                 | I32_NE              [macro] rule I32_NE   => b"x47"
                 | I32_LT_S            [macro] rule I32_LT_S => b"x48"
                 | I32_LT_U            [macro] rule I32_LT_U => b"x49"
                 | I32_GT_S            [macro] rule I32_GT_S => b"x4A"
                 | I32_GT_U            [macro] rule I32_GT_U => b"x4B"
                 | I32_LE_S            [macro] rule I32_LE_S => b"x4C"
                 | I32_LE_U            [macro] rule I32_LE_U => b"x4D"
                 | I32_GE_S            [macro] rule I32_GE_S => b"x4E"
                 | I32_GE_U            [macro] rule I32_GE_U => b"x4F"

                 | I64_EQZ             [macro] rule I64_EQZ  => b"x50"
                 | I64_EQ              [macro] rule I64_EQ   => b"x51"
                 | I64_NE              [macro] rule I64_NE   => b"x52"
                 | I64_LT_S            [macro] rule I64_LT_S => b"x53"
                 | I64_LT_U            [macro] rule I64_LT_U => b"x54"
                 | I64_GT_S            [macro] rule I64_GT_S => b"x55"
                 | I64_GT_U            [macro] rule I64_GT_U => b"x56"
                 | I64_LE_S            [macro] rule I64_LE_S => b"x57"
                 | I64_LE_U            [macro] rule I64_LE_U => b"x58"
                 | I64_GE_S            [macro] rule I64_GE_S => b"x59"
                 | I64_GE_U            [macro] rule I64_GE_U => b"x5A"

                 | F32_EQ              [macro] rule F32_EQ => b"x5B"
                 | F32_NE              [macro] rule F32_NE => b"x5C"
                 | F32_LT              [macro] rule F32_LT => b"x5D"
                 | F32_GT              [macro] rule F32_GT => b"x5E"
                 | F32_LE              [macro] rule F32_LE => b"x5F"
                 | F32_GE              [macro] rule F32_GE => b"x60"

                 | F64_EQ              [macro] rule F64_EQ => b"x61"
                 | F64_NE              [macro] rule F64_NE => b"x62"
                 | F64_LT              [macro] rule F64_LT => b"x63"
                 | F64_GT              [macro] rule F64_GT => b"x64"
                 | F64_LE              [macro] rule F64_LE => b"x65"
                 | F64_GE              [macro] rule F64_GE => b"x66"

                 | I32_CLZ             [macro]
                 | I32_CTZ             [macro]
                 | I32_POPCNT          [macro]
                 | I32_ADD             [macro]
                 | I32_SUB             [macro]
                 | I32_MUL             [macro]
                 | I32_DIV_S           [macro]
                 | I32_DIV_U           [macro]
                 | I32_REM_S           [macro]
                 | I32_REM_U           [macro]
                 | I32_AND             [macro]
                 | I32_OR              [macro]
                 | I32_XOR             [macro]
                 | I32_SHL             [macro]
                 | I32_SHR_S           [macro]
                 | I32_SHR_U           [macro]
                 | I32_ROTL            [macro]
                 | I32_ROTR            [macro]

                 | I64_CLZ             [macro]
                 | I64_CTZ             [macro]
                 | I64_POPCNT          [macro]
                 | I64_ADD             [macro]
                 | I64_SUB             [macro]
                 | I64_MUL             [macro]
                 | I64_DIV_S           [macro]
                 | I64_DIV_U           [macro]
                 | I64_REM_S           [macro]
                 | I64_REM_U           [macro]
                 | I64_AND             [macro]
                 | I64_OR              [macro]
                 | I64_XOR             [macro]
                 | I64_SHL             [macro]
                 | I64_SHR_S           [macro]
                 | I64_SHR_U           [macro]
                 | I64_ROTL            [macro]
                 | I64_ROTR            [macro]

                 | F32_ABS             [macro]
                 | F32_NEG             [macro]
                 | F32_CEIL            [macro]
                 | F32_FLOOR           [macro]
                 | F32_TRUNC           [macro]
                 | F32_NEARSET         [macro]
                 | F32_SQRT            [macro]
                 | F32_ADD             [macro]
                 | F32_SUB             [macro]
                 | F32_MUL             [macro]
                 | F32_DIV             [macro]
                 | F32_MIN             [macro]
                 | F32_MAX             [macro]
                 | F32_COPYSIGN        [macro]

                 | F64_ABS             [macro]
                 | F64_NEG             [macro]
                 | F64_CEIL            [macro]
                 | F64_FLOOR           [macro]
                 | F64_TRUNC           [macro]
                 | F64_NEARSET         [macro]
                 | F64_SQRT            [macro]
                 | F64_ADD             [macro]
                 | F64_SUB             [macro]
                 | F64_MUL             [macro]
                 | F64_DIV             [macro]
                 | F64_MIN             [macro]
                 | F64_MAX             [macro]
                 | F64_COPYSIGN        [macro]

                 | I32_WRAP_I64        [macro]
                 | I32_TRUNC_F32_S     [macro]
                 | I32_TRUNC_F32_U     [macro]
                 | I32_TRUNC_F64_S     [macro]
                 | I32_TRUNC_F64_U     [macro]

                 | I64_EXTEND_I32_S    [macro]
                 | I64_EXTEND_I32_U    [macro]
                 | I64_TRUNC_F32_S     [macro]
                 | I64_TRUNC_F32_U     [macro]
                 | I64_TRUNC_F64_S     [macro]
                 | I64_TRUNC_F64_U     [macro]

                 | F32_CONVERT_I32_S   [macro]
                 | F32_CONVERT_I32_U   [macro]
                 | F32_CONVERT_I64_S   [macro]
                 | F32_CONVERT_I64_U   [macro]
                 | F32_DEMOTE_F64      [macro]

                 | F64_CONVERT_I32_S   [macro]
                 | F64_CONVERT_I32_U   [macro]
                 | F64_CONVERT_I64_S   [macro]
                 | F64_CONVERT_I64_U   [macro]
                 | F64_PROMOTE_F32     [macro]

                 | I32_REINTERPRET_F32 [macro]
                 | I64_REINTERPRET_F64 [macro]
                 | F32_REINTERPRET_I32 [macro]
                 | F64_REINTERPRET_I64 [macro]

                 | I32_EXTEND_8_S      [macro]
                 | I32_EXTEND_16_S     [macro]
                 | I64_EXTEND_8_S      [macro]
                 | I64_EXTEND_16_S     [macro]
                 | I64_EXTEND_32_S     [macro]
```

```k
endmodule
```

module BINARY_PARSER [private]
  imports WASM
  imports BINARY_PARSER_DATA

  syntax ParseResult ::= ModuleDecl
                       | ParseError(String)


  syntax ModuleDecl ::= parseModule(Bytes)  [function, total]
                      | parseMagic(Bytes)   [function, total]
                      | parseVersion(Bytes) [function, total]

endmodule
