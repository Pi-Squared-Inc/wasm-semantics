# Wasm Binary Parser

This file defines a Wasm binary parser based on this
[spec](https://webassembly.github.io/spec/core/binary/index.html).
To begin, we define constant macros which drive the parser process.

```k

requires "binary-parser-base.md"
requires "binary-parser-instrs.md"

module BINARY-PARSER-DATA
  imports BYTES
  imports INT
```

## Wasm Metadata Parser Tags

Every Wasm module starts with a 4-byte header and a 4-byte version.

```k
  syntax Bytes ::= "MAGIC"   [macro] rule MAGIC   => b"\x00\x61\x73\x6D"
  syntax Bytes ::= "VERSION" [macro] rule VERSION => b"\x01\x00\x00\x00"
```

After that, a Wasm module is an ordered list of sections, each prefixed with a section id.

```k
  syntax Int ::= "CUSTOM_SEC" [macro] rule CUSTOM_SEC => 0
  syntax Int ::= "TYPE_SEC"   [macro] rule TYPE_SEC   => 1
  syntax Int ::= "IMPORT_SEC" [macro] rule IMPORT_SEC => 2
  syntax Int ::= "FUNC_SEC"   [macro] rule FUNC_SEC   => 3
  syntax Int ::= "TABLE_SEC"  [macro] rule TABLE_SEC  => 4
  syntax Int ::= "MEMORY_SEC" [macro] rule MEMORY_SEC => 5
  syntax Int ::= "GLOBAL_SEC" [macro] rule GLOBAL_SEC => 6
  syntax Int ::= "EXPORT_SEC" [macro] rule EXPORT_SEC => 7
  syntax Int ::= "START_SEC"  [macro] rule START_SEC  => 8
  syntax Int ::= "ELT_SEC"    [macro] rule ELT_SEC    => 9
  syntax Int ::= "CODE_SEC"   [macro] rule CODE_SEC   => 10
  syntax Int ::= "DAT_SEC"    [macro] rule DAT_SEC    => 11
  syntax Int ::= "CNT_SEC"    [macro] rule CNT_SEC    => 12
```

In the import/export sections, different kinds of imports/exports are tagged.

```k
  syntax Bytes ::= "IMPORT_FUNC" [macro] rule IMPORT_FUNC => b"\x00"
  syntax Bytes ::= "IMPORT_TBLT" [macro] rule IMPORT_TBLT => b"\x01"
  syntax Bytes ::= "IMPORT_MEMT" [macro] rule IMPORT_MEMT => b"\x02"
  syntax Bytes ::= "IMPORT_GLBT" [macro] rule IMPORT_GLBT => b"\x03"
  syntax Bytes ::= "EXPORT_FUNC" [macro] rule EXPORT_FUNC => b"\x00"
  syntax Bytes ::= "EXPORT_TBLT" [macro] rule EXPORT_TBLT => b"\x01"
  syntax Bytes ::= "EXPORT_MEMT" [macro] rule EXPORT_MEMT => b"\x02"
  syntax Bytes ::= "EXPORT_GLBT" [macro] rule EXPORT_GLBT => b"\x03"
```

_Element_ sections have various possible formats which are stored in a 3-bit code.
The possible code words are explained in the table below:

Bit # | "C"onstraint | "0" State         | "1" State              |
----- | ---------- | --------------- | -------------------- |
0     | "N"one       | active          | passive/declarative  |
1     | "B"it[0]=0   | has table index | zero table index     |
1     | "B"it[0]=1   | passive         | declarative          |
2     | "N"one       | elts by ref     | elts by value        |

```k
  syntax Bytes ::= "ELTS_ACTIVE_ZERO_BY_REF" [macro] // 000
  syntax Bytes ::= "ELTS_PASSIVE_BY_REF"     [macro] // 001
  syntax Bytes ::= "ELTS_ACTIVE_IDX_BY_REF"  [macro] // 010
  syntax Bytes ::= "ELTS_DECL_BY_REF"        [macro] // 011
  syntax Bytes ::= "ELTS_ACTIVE_ZERO_BY_VAL" [macro] // 100
  syntax Bytes ::= "ELTS_PASSIVE_BY_VAL"     [macro] // 101
  syntax Bytes ::= "ELTS_ACTIVE_IDX_BY_VAL"  [macro] // 110
  syntax Bytes ::= "ELTS_DECL_BY_VAL"        [macro] // 110

  rule ELTS_ACTIVE_ZERO_BY_REF => b"\x00"
  rule ELTS_PASSIVE_BY_REF     => b"\x01"
  rule ELTS_ACTIVE_IDX_BY_REF  => b"\x02"
  rule ELTS_DECL_BY_REF        => b"\x03"
  rule ELTS_ACTIVE_ZERO_BY_VAL => b"\x04"
  rule ELTS_PASSIVE_BY_VAL     => b"\x05"
  rule ELTS_ACTIVE_IDX_BY_VAL  => b"\x06"
  rule ELTS_DECL_BY_VAL        => b"\x07"
```

The special _element kind_ constant is used to describe possible element kinds.
Currently, only one element kind is supported.

```k
  syntax Bytes ::= "ELT_KIND" [macro] rule ELT_KIND => b"\x00"
```

_Data_ sections are tagged based on their kind.

```k
  syntax Bytes ::= "DATA_ACTIVE_ZERO" [macro] rule DATA_ACTIVE_ZERO  => b"\x00"
  syntax Bytes ::= "DATA_PASSIVE"     [macro] rule DATA_PASSIVE => b"\x01"
  syntax Bytes ::= "DATA_ACTIVE_IDX"  [macro] rule DATA_ACTIVE_IDX   => b"\x02"
```

Each value _type_ is tagged by a unique integer.
There are two special types: functions and empty types.
These have special use requirements as we will see later.

```k
  syntax Bytes ::= "TYPE_I32"     [macro] rule TYPE_I32     => b"\x7F"
  syntax Bytes ::= "TYPE_I64"     [macro] rule TYPE_I64     => b"\x7E"
  syntax Bytes ::= "TYPE_F32"     [macro] rule TYPE_F32     => b"\x7D"
  syntax Bytes ::= "TYPE_F64"     [macro] rule TYPE_F64     => b"\x7C"
  syntax Bytes ::= "TYPE_VEC"     [macro] rule TYPE_VEC     => b"\x7B"
  syntax Bytes ::= "TYPE_FUN_REF" [macro] rule TYPE_FUN_REF => b"\x70"
  syntax Bytes ::= "TYPE_EXT_REF" [macro] rule TYPE_EXT_REF => b"\x6F"
  syntax Bytes ::= "TYPE_FUN"     [macro] rule TYPE_FUN     => b"\x60"
  syntax Bytes ::= "TYPE_EMPTY"   [macro] rule TYPE_EMPTY   => b"\x40"
```

_Limits_ are used to encode the minimum size of memories and tables;
a separate form that also specifies a maximum size is available.

```k
  syntax Bytes ::= "LIMITS_MIN" [macro] rule LIMITS_MIN => b"\x00"
  syntax Bytes ::= "LIMITS"     [macro] rule LIMITS     => b"\x01"
```

_Globals_ may be declared as mutable or immutable.

```k
  syntax Bytes ::= "GLOBAL_CNST" [macro] rule GLOBAL_CNST => b"\x00"
  syntax Bytes ::= "GLOBAL_VAR"  [macro] rule GLOBAL_VAR  => b"\x01"
```

## Wasm Instruction Parser Tags

Wasm _control instructions_ are encoded with the follow tags.
Note that `ELSE` instructions must appear in conjunction with `IF` instructions.

```k
  syntax Bytes ::= "UNREACHABLE"   [macro] rule UNREACHABLE   => b"\x00"
  syntax Bytes ::= "NOP"           [macro] rule NOP           => b"\x01"
  syntax Bytes ::= "BLOCK"         [macro] rule BLOCK         => b"\x02"
  syntax Bytes ::= "LOOP"          [macro] rule LOOP          => b"\x03"
  syntax Bytes ::= "IF"            [macro] rule IF            => b"\x04"
  syntax Bytes ::= "ELSE"          [macro] rule ELSE          => b"\x05"
  syntax Bytes ::= "BR"            [macro] rule BR            => b"\x0C"
  syntax Bytes ::= "BR_IF"         [macro] rule BR_IF         => b"\x0D"
  syntax Bytes ::= "BR_TABLE"      [macro] rule BR_TABLE      => b"\x0E"
  syntax Bytes ::= "RETURN"        [macro] rule RETURN        => b"\x0F"
  syntax Bytes ::= "CALL"          [macro] rule CALL          => b"\x10"
  syntax Bytes ::= "CALL_INDIRECT" [macro] rule CALL_INDIRECT => b"\x11"
```

_Reference instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= "REF_NULL"   [macro] rule REF_NULL   => b"\xD0"
  syntax Bytes ::= "REF_ISNULL" [macro] rule REF_ISNULL => b"\xD1"
  syntax Bytes ::= "REF_FUNC"   [macro] rule REF_FUNC   => b"\xD2"
```

```k
  syntax Bytes ::= "DROP"           [macro] rule DROP           => b"\x1A"
  syntax Bytes ::= "SELECT"         [macro] rule SELECT         => b"\x1B"
  syntax Bytes ::= "SELECT_GENERIC" [macro] rule SELECT_GENERIC => b"\x1C"
```

_Variable instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= "LOCAL_GET"  [macro] rule LOCAL_GET  => b"\x20"
  syntax Bytes ::= "LOCAL_SET"  [macro] rule LOCAL_SET  => b"\x21"
  syntax Bytes ::= "LOCAL_TEE"  [macro] rule LOCAL_TEE  => b"\x22"
  syntax Bytes ::= "GLOBAL_GET" [macro] rule GLOBAL_GET => b"\x23"
  syntax Bytes ::= "GLOBAL_SET" [macro] rule GLOBAL_SET => b"\x24"
```

_Table instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= "TABLE_GET"  [macro] rule TABLE_GET  => b"\x25"
  syntax Bytes ::= "TABLE_SET"  [macro] rule TABLE_SET  => b"\x26"
  syntax Bytes ::= "TABLE_INIT" [macro] rule TABLE_INIT => b"\xFC\x0C"
  syntax Bytes ::= "ELEM_DROP"  [macro] rule ELEM_DROP  => b"\xFC\x0D"
  syntax Bytes ::= "TABLE_COPY" [macro] rule TABLE_COPY => b"\xFC\x0E"
  syntax Bytes ::= "TABLE_GROW" [macro] rule TABLE_GROW => b"\xFC\x0F"
  syntax Bytes ::= "TABLE_SIZE" [macro] rule TABLE_SIZE => b"\xFC\x10"
  syntax Bytes ::= "TABLE_FILL" [macro] rule TABLE_FILL => b"\xFC\x11"
```

_Memory instructions_ are encoded with the following tags:

```k
  syntax Bytes ::= "I32_LOAD"      [macro] rule I32_LOAD      => b"\x28"
  syntax Bytes ::= "I64_LOAD"      [macro] rule I64_LOAD      => b"\x29"
  syntax Bytes ::= "F32_LOAD"      [macro] rule F32_LOAD      => b"\x2A"
  syntax Bytes ::= "F64_LOAD"      [macro] rule F64_LOAD      => b"\x2B"
  syntax Bytes ::= "I32_LOAD_8_S"  [macro] rule I32_LOAD_8_S  => b"\x2C"
  syntax Bytes ::= "I32_LOAD_8_U"  [macro] rule I32_LOAD_8_U  => b"\x2D"
  syntax Bytes ::= "I32_LOAD_16_S" [macro] rule I32_LOAD_16_S => b"\x2E"
  syntax Bytes ::= "I32_LOAD_16_U" [macro] rule I32_LOAD_16_U => b"\x2F"
  syntax Bytes ::= "I64_LOAD_8_S"  [macro] rule I64_LOAD_8_S  => b"\x30"
  syntax Bytes ::= "I64_LOAD_8_U"  [macro] rule I64_LOAD_8_U  => b"\x31"
  syntax Bytes ::= "I64_LOAD_16_S" [macro] rule I64_LOAD_16_S => b"\x32"
  syntax Bytes ::= "I64_LOAD_16_U" [macro] rule I64_LOAD_16_U => b"\x33"
  syntax Bytes ::= "I64_LOAD_32_S" [macro] rule I64_LOAD_32_S => b"\x34"
  syntax Bytes ::= "I64_LOAD_32_U" [macro] rule I64_LOAD_32_U => b"\x35"
  syntax Bytes ::= "I32_STORE"     [macro] rule I32_STORE     => b"\x36"
  syntax Bytes ::= "I64_STORE"     [macro] rule I64_STORE     => b"\x37"
  syntax Bytes ::= "F32_STORE"     [macro] rule F32_STORE     => b"\x38"
  syntax Bytes ::= "F64_STORE"     [macro] rule F64_STORE     => b"\x39"
  syntax Bytes ::= "I32_STORE_8"   [macro] rule I32_STORE_8   => b"\x3A"
  syntax Bytes ::= "I32_STORE_16"  [macro] rule I32_STORE_16  => b"\x3B"
  syntax Bytes ::= "I64_STORE_8"   [macro] rule I64_STORE_8   => b"\x3C"
  syntax Bytes ::= "I64_STORE_16"  [macro] rule I64_STORE_16  => b"\x3D"
  syntax Bytes ::= "I64_STORE_32"  [macro] rule I64_STORE_32  => b"\x3E"
  syntax Bytes ::= "MEM_SIZE"      [macro] rule MEM_SIZE      => b"\x3F"
  syntax Bytes ::= "MEM_GROW"      [macro] rule MEM_GROW      => b"\x40"
  syntax Bytes ::= "MEM_INIT"      [macro] rule MEM_INIT      => b"\xFC\x08"
  syntax Bytes ::= "DATA_DROP"     [macro] rule DATA_DROP     => b"\xFC\x09"
  syntax Bytes ::= "MEM_COPY"      [macro] rule MEM_COPY      => b"\xFC\x0A"
  syntax Bytes ::= "MEM_FILL"      [macro] rule MEM_FILL      => b"\xFC\x0B"
```

_Numeric instructions_ have the following tags:

```k
  syntax Bytes ::= "I32_CONST"           [macro] rule I32_CONST => b"\x41"
  syntax Bytes ::= "I64_CONST"           [macro] rule I64_CONST => b"\x42"
  syntax Bytes ::= "F32_CONST"           [macro] rule F32_CONST => b"\x43"
  syntax Bytes ::= "F64_CONST"           [macro] rule F64_CONST => b"\x44"

  syntax Bytes ::= "I32_EQZ"             [macro] rule I32_EQZ  => b"\x45"
  syntax Bytes ::= "I32_EQ"              [macro] rule I32_EQ   => b"\x46"
  syntax Bytes ::= "I32_NE"              [macro] rule I32_NE   => b"\x47"
  syntax Bytes ::= "I32_LT_S"            [macro] rule I32_LT_S => b"\x48"
  syntax Bytes ::= "I32_LT_U"            [macro] rule I32_LT_U => b"\x49"
  syntax Bytes ::= "I32_GT_S"            [macro] rule I32_GT_S => b"\x4A"
  syntax Bytes ::= "I32_GT_U"            [macro] rule I32_GT_U => b"\x4B"
  syntax Bytes ::= "I32_LE_S"            [macro] rule I32_LE_S => b"\x4C"
  syntax Bytes ::= "I32_LE_U"            [macro] rule I32_LE_U => b"\x4D"
  syntax Bytes ::= "I32_GE_S"            [macro] rule I32_GE_S => b"\x4E"
  syntax Bytes ::= "I32_GE_U"            [macro] rule I32_GE_U => b"\x4F"

  syntax Bytes ::= "I64_EQZ"             [macro] rule I64_EQZ  => b"\x50"
  syntax Bytes ::= "I64_EQ"              [macro] rule I64_EQ   => b"\x51"
  syntax Bytes ::= "I64_NE"              [macro] rule I64_NE   => b"\x52"
  syntax Bytes ::= "I64_LT_S"            [macro] rule I64_LT_S => b"\x53"
  syntax Bytes ::= "I64_LT_U"            [macro] rule I64_LT_U => b"\x54"
  syntax Bytes ::= "I64_GT_S"            [macro] rule I64_GT_S => b"\x55"
  syntax Bytes ::= "I64_GT_U"            [macro] rule I64_GT_U => b"\x56"
  syntax Bytes ::= "I64_LE_S"            [macro] rule I64_LE_S => b"\x57"
  syntax Bytes ::= "I64_LE_U"            [macro] rule I64_LE_U => b"\x58"
  syntax Bytes ::= "I64_GE_S"            [macro] rule I64_GE_S => b"\x59"
  syntax Bytes ::= "I64_GE_U"            [macro] rule I64_GE_U => b"\x5A"

  syntax Bytes ::= "F32_EQ"              [macro] rule F32_EQ => b"\x5B"
  syntax Bytes ::= "F32_NE"              [macro] rule F32_NE => b"\x5C"
  syntax Bytes ::= "F32_LT"              [macro] rule F32_LT => b"\x5D"
  syntax Bytes ::= "F32_GT"              [macro] rule F32_GT => b"\x5E"
  syntax Bytes ::= "F32_LE"              [macro] rule F32_LE => b"\x5F"
  syntax Bytes ::= "F32_GE"              [macro] rule F32_GE => b"\x60"

  syntax Bytes ::= "F64_EQ"              [macro] rule F64_EQ => b"\x61"
  syntax Bytes ::= "F64_NE"              [macro] rule F64_NE => b"\x62"
  syntax Bytes ::= "F64_LT"              [macro] rule F64_LT => b"\x63"
  syntax Bytes ::= "F64_GT"              [macro] rule F64_GT => b"\x64"
  syntax Bytes ::= "F64_LE"              [macro] rule F64_LE => b"\x65"
  syntax Bytes ::= "F64_GE"              [macro] rule F64_GE => b"\x66"

  syntax Bytes ::= "I32_CLZ"             [macro] rule I32_CLZ => b"\x67"
  syntax Bytes ::= "I32_CTZ"             [macro] rule I32_CTZ => b"\x68"
  syntax Bytes ::= "I32_POPCNT"          [macro] rule I32_POPCNT => b"\x69"
  syntax Bytes ::= "I32_ADD"             [macro] rule I32_ADD => b"\x6A"
  syntax Bytes ::= "I32_SUB"             [macro] rule I32_SUB => b"\x6B"
  syntax Bytes ::= "I32_MUL"             [macro] rule I32_MUL => b"\x6C"
  syntax Bytes ::= "I32_DIV_S"           [macro] rule I32_DIV_S => b"\x6D"
  syntax Bytes ::= "I32_DIV_U"           [macro] rule I32_DIV_U => b"\x6E"
  syntax Bytes ::= "I32_REM_S"           [macro] rule I32_REM_S => b"\x6F"
  syntax Bytes ::= "I32_REM_U"           [macro] rule I32_REM_U => b"\x70"
  syntax Bytes ::= "I32_AND"             [macro] rule I32_AND => b"\x71"
  syntax Bytes ::= "I32_OR"              [macro] rule I32_OR => b"\x72"
  syntax Bytes ::= "I32_XOR"             [macro] rule I32_XOR => b"\x73"
  syntax Bytes ::= "I32_SHL"             [macro] rule I32_SHL => b"\x74"
  syntax Bytes ::= "I32_SHR_S"           [macro] rule I32_SHR_S => b"\x75"
  syntax Bytes ::= "I32_SHR_U"           [macro] rule I32_SHR_U => b"\x76"
  syntax Bytes ::= "I32_ROTL"            [macro] rule I32_ROTL => b"\x77"
  syntax Bytes ::= "I32_ROTR"            [macro] rule I32_ROTR => b"\x78"

  syntax Bytes ::= "I64_CLZ"             [macro] rule I64_CLZ => b"\x79"
  syntax Bytes ::= "I64_CTZ"             [macro] rule I64_CTZ => b"\x7A"
  syntax Bytes ::= "I64_POPCNT"          [macro] rule I64_POPCNT => b"\x7B"
  syntax Bytes ::= "I64_ADD"             [macro] rule I64_ADD => b"\x7C"
  syntax Bytes ::= "I64_SUB"             [macro] rule I64_SUB => b"\x7D"
  syntax Bytes ::= "I64_MUL"             [macro] rule I64_MUL => b"\x7E"
  syntax Bytes ::= "I64_DIV_S"           [macro] rule I64_DIV_S => b"\x7F"
  syntax Bytes ::= "I64_DIV_U"           [macro] rule I64_DIV_U => b"\x80"
  syntax Bytes ::= "I64_REM_S"           [macro] rule I64_REM_S => b"\x81"
  syntax Bytes ::= "I64_REM_U"           [macro] rule I64_REM_U => b"\x82"
  syntax Bytes ::= "I64_AND"             [macro] rule I64_AND => b"\x83"
  syntax Bytes ::= "I64_OR"              [macro] rule I64_OR => b"\x84"
  syntax Bytes ::= "I64_XOR"             [macro] rule I64_XOR => b"\x85"
  syntax Bytes ::= "I64_SHL"             [macro] rule I64_SHL => b"\x86"
  syntax Bytes ::= "I64_SHR_S"           [macro] rule I64_SHR_S => b"\x87"
  syntax Bytes ::= "I64_SHR_U"           [macro] rule I64_SHR_U => b"\x88"
  syntax Bytes ::= "I64_ROTL"            [macro] rule I64_ROTL => b"\x89"
  syntax Bytes ::= "I64_ROTR"            [macro] rule I64_ROTR => b"\x8A"

  syntax Bytes ::= "F32_ABS"             [macro] rule F32_ABS => b"\x8B"
  syntax Bytes ::= "F32_NEG"             [macro] rule F32_NEG => b"\x8C"
  syntax Bytes ::= "F32_CEIL"            [macro] rule F32_CEIL => b"\x8D"
  syntax Bytes ::= "F32_FLOOR"           [macro] rule F32_FLOOR => b"\x8E"
  syntax Bytes ::= "F32_TRUNC"           [macro] rule F32_TRUNC => b"\x8F"
  syntax Bytes ::= "F32_NEAREST"         [macro] rule F32_NEAREST => b"\x90"
  syntax Bytes ::= "F32_SQRT"            [macro] rule F32_SQRT => b"\x91"
  syntax Bytes ::= "F32_ADD"             [macro] rule F32_ADD => b"\x92"
  syntax Bytes ::= "F32_SUB"             [macro] rule F32_SUB => b"\x93"
  syntax Bytes ::= "F32_MUL"             [macro] rule F32_MUL => b"\x94"
  syntax Bytes ::= "F32_DIV"             [macro] rule F32_DIV => b"\x95"
  syntax Bytes ::= "F32_MIN"             [macro] rule F32_MIN => b"\x96"
  syntax Bytes ::= "F32_MAX"             [macro] rule F32_MAX => b"\x97"
  syntax Bytes ::= "F32_COPYSIGN"        [macro] rule F32_COPYSIGN => b"\x98"

  syntax Bytes ::= "F64_ABS"             [macro] rule F64_ABS => b"\x99"
  syntax Bytes ::= "F64_NEG"             [macro] rule F64_NEG => b"\x9A"
  syntax Bytes ::= "F64_CEIL"            [macro] rule F64_CEIL => b"\x9B"
  syntax Bytes ::= "F64_FLOOR"           [macro] rule F64_FLOOR => b"\x9C"
  syntax Bytes ::= "F64_TRUNC"           [macro] rule F64_TRUNC => b"\x9D"
  syntax Bytes ::= "F64_NEAREST"         [macro] rule F64_NEAREST => b"\x9E"
  syntax Bytes ::= "F64_SQRT"            [macro] rule F64_SQRT => b"\x9F"
  syntax Bytes ::= "F64_ADD"             [macro] rule F64_ADD => b"\xA0"
  syntax Bytes ::= "F64_SUB"             [macro] rule F64_SUB => b"\xA1"
  syntax Bytes ::= "F64_MUL"             [macro] rule F64_MUL => b"\xA2"
  syntax Bytes ::= "F64_DIV"             [macro] rule F64_DIV => b"\xA3"
  syntax Bytes ::= "F64_MIN"             [macro] rule F64_MIN => b"\xA4"
  syntax Bytes ::= "F64_MAX"             [macro] rule F64_MAX => b"\xA5"
  syntax Bytes ::= "F64_COPYSIGN"        [macro] rule F64_COPYSIGN => b"\xA6"

  syntax Bytes ::= "I32_WRAP_I64"        [macro] rule I32_WRAP_I64 => b"\xA7"
  syntax Bytes ::= "I32_TRUNC_F32_S"     [macro] rule I32_TRUNC_F32_S => b"\xA8"
  syntax Bytes ::= "I32_TRUNC_F32_U"     [macro] rule I32_TRUNC_F32_U => b"\xA9"
  syntax Bytes ::= "I32_TRUNC_F64_S"     [macro] rule I32_TRUNC_F64_S => b"\xAA"
  syntax Bytes ::= "I32_TRUNC_F64_U"     [macro] rule I32_TRUNC_F64_U => b"\xAB"

  syntax Bytes ::= "I64_EXTEND_I32_S"    [macro] rule I64_EXTEND_I32_S => b"\xAC"
  syntax Bytes ::= "I64_EXTEND_I32_U"    [macro] rule I64_EXTEND_I32_U => b"\xAD"
  syntax Bytes ::= "I64_TRUNC_F32_S"     [macro] rule I64_TRUNC_F32_S => b"\xAE"
  syntax Bytes ::= "I64_TRUNC_F32_U"     [macro] rule I64_TRUNC_F32_U => b"\xAF"
  syntax Bytes ::= "I64_TRUNC_F64_S"     [macro] rule I64_TRUNC_F64_S => b"\xB0"
  syntax Bytes ::= "I64_TRUNC_F64_U"     [macro] rule I64_TRUNC_F64_U => b"\xB1"

  syntax Bytes ::= "F32_CONVERT_I32_S"   [macro] rule F32_CONVERT_I32_S => b"\xB2"
  syntax Bytes ::= "F32_CONVERT_I32_U"   [macro] rule F32_CONVERT_I32_U => b"\xB3"
  syntax Bytes ::= "F32_CONVERT_I64_S"   [macro] rule F32_CONVERT_I64_S => b"\xB4"
  syntax Bytes ::= "F32_CONVERT_I64_U"   [macro] rule F32_CONVERT_I64_U => b"\xB5"
  syntax Bytes ::= "F32_DEMOTE_F64"      [macro] rule F32_DEMOTE_F64 => b"\xB6"

  syntax Bytes ::= "F64_CONVERT_I32_S"   [macro] rule F64_CONVERT_I32_S => b"\xB7"
  syntax Bytes ::= "F64_CONVERT_I32_U"   [macro] rule F64_CONVERT_I32_U => b"\xB8"
  syntax Bytes ::= "F64_CONVERT_I64_S"   [macro] rule F64_CONVERT_I64_S => b"\xB9"
  syntax Bytes ::= "F64_CONVERT_I64_U"   [macro] rule F64_CONVERT_I64_U => b"\xBA"
  syntax Bytes ::= "F64_PROMOTE_F32"     [macro] rule F64_PROMOTE_F32 => b"\xBB"

  syntax Bytes ::= "I32_REINTERPRET_F32" [macro] rule I32_REINTERPRET_F32 => b"\xBC"
  syntax Bytes ::= "I64_REINTERPRET_F64" [macro] rule I64_REINTERPRET_F64 => b"\xBD"
  syntax Bytes ::= "F32_REINTERPRET_I32" [macro] rule F32_REINTERPRET_I32 => b"\xBE"
  syntax Bytes ::= "F64_REINTERPRET_I64" [macro] rule F64_REINTERPRET_I64 => b"\xBF"

  syntax Bytes ::= "I32_EXTEND_8_S"      [macro] rule I32_EXTEND_8_S => b"\xC0"
  syntax Bytes ::= "I32_EXTEND_16_S"     [macro] rule I32_EXTEND_16_S => b"\xC1"
  syntax Bytes ::= "I64_EXTEND_8_S"      [macro] rule I64_EXTEND_8_S => b"\xC2"
  syntax Bytes ::= "I64_EXTEND_16_S"     [macro] rule I64_EXTEND_16_S => b"\xC3"
  syntax Bytes ::= "I64_EXTEND_32_S"     [macro] rule I64_EXTEND_32_S => b"\xC4"

  syntax Bytes ::= "I32_TRUNC_SAT_F32_S" [macro] rule I32_TRUNC_SAT_F32_S => b"\xFC\x00"
  syntax Bytes ::= "I32_TRUNC_SAT_F32_U" [macro] rule I32_TRUNC_SAT_F32_U => b"\xFC\x01"
  syntax Bytes ::= "I32_TRUNC_SAT_F64_S" [macro] rule I32_TRUNC_SAT_F64_S => b"\xFC\x02"
  syntax Bytes ::= "I32_TRUNC_SAT_F64_U" [macro] rule I32_TRUNC_SAT_F64_U => b"\xFC\x03"
  syntax Bytes ::= "I64_TRUNC_SAT_F32_S" [macro] rule I64_TRUNC_SAT_F32_S => b"\xFC\x04"
  syntax Bytes ::= "I64_TRUNC_SAT_F32_U" [macro] rule I64_TRUNC_SAT_F32_U => b"\xFC\x05"
  syntax Bytes ::= "I64_TRUNC_SAT_F64_S" [macro] rule I64_TRUNC_SAT_F64_S => b"\xFC\x06"
  syntax Bytes ::= "I64_TRUNC_SAT_F64_U" [macro] rule I64_TRUNC_SAT_F64_U => b"\xFC\x07"
```

_Vector instructions_ have the following tags:

```k

  syntax Bytes ::= "V128_LOAD" [macro] rule V128_LOAD => b"\xFD\x00"
  syntax Bytes ::= "V128_LOAD_8X8_S" [macro] rule V128_LOAD_8X8_S => b"\xFD\x01"
  syntax Bytes ::= "V128_LOAD_8X8_U" [macro] rule V128_LOAD_8X8_U => b"\xFD\x02"
  syntax Bytes ::= "V128_LOAD_16X4_S" [macro] rule V128_LOAD_16X4_S => b"\xFD\x03"
  syntax Bytes ::= "V128_LOAD_16X4_U" [macro] rule V128_LOAD_16X4_U => b"\xFD\x04"
  syntax Bytes ::= "V128_LOAD_32X2_S" [macro] rule V128_LOAD_32X2_S => b"\xFD\x05"
  syntax Bytes ::= "V128_LOAD_32X2_U" [macro] rule V128_LOAD_32X2_U => b"\xFD\x06"
  syntax Bytes ::= "V128_LOAD_8_SPLAT" [macro] rule V128_LOAD_8_SPLAT => b"\xFD\x07"
  syntax Bytes ::= "V128_LOAD_16_SPLAT" [macro] rule V128_LOAD_16_SPLAT => b"\xFD\x08"
  syntax Bytes ::= "V128_LOAD_32_SPLAT" [macro] rule V128_LOAD_32_SPLAT => b"\xFD\x09"
  syntax Bytes ::= "V128_LOAD_64_SPLAT" [macro] rule V128_LOAD_64_SPLAT => b"\xFD\x0A"
  syntax Bytes ::= "V128_LOAD_32_ZERO" [macro] rule V128_LOAD_32_ZERO => b"\xFD\x5C"
  syntax Bytes ::= "V128_LOAD_64_ZERO" [macro] rule V128_LOAD_64_ZERO => b"\xFD\x5D"
  syntax Bytes ::= "V128_STORE" [macro] rule V128_STORE => b"\xFD\x0B"
  syntax Bytes ::= "V128_LOAD_8_LANE" [macro] rule V128_LOAD_8_LANE => b"\xFD\x54"
  syntax Bytes ::= "V128_LOAD_16_LANE" [macro] rule V128_LOAD_16_LANE => b"\xFD\x55"
  syntax Bytes ::= "V128_LOAD_32_LANE" [macro] rule V128_LOAD_32_LANE => b"\xFD\x56"
  syntax Bytes ::= "V128_LOAD_64_LANE" [macro] rule V128_LOAD_64_LANE => b"\xFD\x57"
  syntax Bytes ::= "V128_STORE_8_LANE" [macro] rule V128_STORE_8_LANE => b"\xFD\x58"
  syntax Bytes ::= "V128_STORE_16_LANE" [macro] rule V128_STORE_16_LANE => b"\xFD\x59"
  syntax Bytes ::= "V128_STORE_32_LANE" [macro] rule V128_STORE_32_LANE => b"\xFD\x5A"
  syntax Bytes ::= "V128_STORE_64_LANE" [macro] rule V128_STORE_64_LANE => b"\xFD\x5B"

  syntax Bytes ::= "V128_CONST_BYTES" [macro] rule V128_CONST_BYTES => b"\xFD\x0C"

  syntax Bytes ::= "I8X16_SHUFFLE" [macro] rule I8X16_SHUFFLE => b"\xFD\x0D"

  syntax Bytes ::= "I8X16_EXTRACT_LANE_S" [macro] rule I8X16_EXTRACT_LANE_S => b"\xFD\x15"
  syntax Bytes ::= "I8X16_EXTRACT_LANE_U" [macro] rule I8X16_EXTRACT_LANE_U => b"\xFD\x16"
  syntax Bytes ::= "I8X16_REPLACE_LANE" [macro] rule I8X16_REPLACE_LANE => b"\xFD\x17"
  syntax Bytes ::= "I16X8_EXTRACT_LANE_S" [macro] rule I16X8_EXTRACT_LANE_S => b"\xFD\x18"
  syntax Bytes ::= "I16X8_EXTRACT_LANE_U" [macro] rule I16X8_EXTRACT_LANE_U => b"\xFD\x19"
  syntax Bytes ::= "I16X8_REPLACE_LANE" [macro] rule I16X8_REPLACE_LANE => b"\xFD\x1A"
  syntax Bytes ::= "I32X4_EXTRACT_LANE" [macro] rule I32X4_EXTRACT_LANE => b"\xFD\x1B"
  syntax Bytes ::= "I32X4_REPLACE_LANE" [macro] rule I32X4_REPLACE_LANE => b"\xFD\x1C"
  syntax Bytes ::= "I64X2_EXTRACT_LANE" [macro] rule I64X2_EXTRACT_LANE => b"\xFD\x1D"
  syntax Bytes ::= "I64X2_REPLACE_LANE" [macro] rule I64X2_REPLACE_LANE => b"\xFD\x1E"
  syntax Bytes ::= "F32X4_EXTRACT_LANE" [macro] rule F32X4_EXTRACT_LANE => b"\xFD\x1F"
  syntax Bytes ::= "F32X4_REPLACE_LANE" [macro] rule F32X4_REPLACE_LANE => b"\xFD\x20"
  syntax Bytes ::= "F64X2_EXTRACT_LANE" [macro] rule F64X2_EXTRACT_LANE => b"\xFD\x21"
  syntax Bytes ::= "F64X2_REPLACE_LANE" [macro] rule F64X2_REPLACE_LANE => b"\xFD\x22"

  syntax Bytes ::= "I8X16_SWIZZLE" [macro] rule I8X16_SWIZZLE => b"\xFD\x0E"
  syntax Bytes ::= "I8X16_SPLAT" [macro] rule I8X16_SPLAT => b"\xFD\x0F"
  syntax Bytes ::= "I16X8_SPLAT" [macro] rule I16X8_SPLAT => b"\xFD\x10"
  syntax Bytes ::= "I32X4_SPLAT" [macro] rule I32X4_SPLAT => b"\xFD\x11"
  syntax Bytes ::= "I64X2_SPLAT" [macro] rule I64X2_SPLAT => b"\xFD\x12"
  syntax Bytes ::= "F32X4_SPLAT" [macro] rule F32X4_SPLAT => b"\xFD\x13"
  syntax Bytes ::= "F64X2_SPLAT" [macro] rule F64X2_SPLAT => b"\xFD\x14"

  syntax Bytes ::= "I8X16_EQ" [macro] rule I8X16_EQ => b"\xFD\x23"
  syntax Bytes ::= "I8X16_NE" [macro] rule I8X16_NE => b"\xFD\x24"
  syntax Bytes ::= "I8X16_LT_S" [macro] rule I8X16_LT_S => b"\xFD\x25"
  syntax Bytes ::= "I8X16_LT_U" [macro] rule I8X16_LT_U => b"\xFD\x26"
  syntax Bytes ::= "I8X16_GT_S" [macro] rule I8X16_GT_S => b"\xFD\x27"
  syntax Bytes ::= "I8X16_GT_U" [macro] rule I8X16_GT_U => b"\xFD\x28"
  syntax Bytes ::= "I8X16_LE_S" [macro] rule I8X16_LE_S => b"\xFD\x29"
  syntax Bytes ::= "I8X16_LE_U" [macro] rule I8X16_LE_U => b"\xFD\x2A"
  syntax Bytes ::= "I8X16_GE_S" [macro] rule I8X16_GE_S => b"\xFD\x2B"
  syntax Bytes ::= "I8X16_GE_U" [macro] rule I8X16_GE_U => b"\xFD\x2C"

  syntax Bytes ::= "I16X8_EQ" [macro] rule I16X8_EQ => b"\xFD\x2D"
  syntax Bytes ::= "I16X8_NE" [macro] rule I16X8_NE => b"\xFD\x2E"
  syntax Bytes ::= "I16X8_LT_S" [macro] rule I16X8_LT_S => b"\xFD\x2F"
  syntax Bytes ::= "I16X8_LT_U" [macro] rule I16X8_LT_U => b"\xFD\x30"
  syntax Bytes ::= "I16X8_GT_S" [macro] rule I16X8_GT_S => b"\xFD\x31"
  syntax Bytes ::= "I16X8_GT_U" [macro] rule I16X8_GT_U => b"\xFD\x32"
  syntax Bytes ::= "I16X8_LE_S" [macro] rule I16X8_LE_S => b"\xFD\x33"
  syntax Bytes ::= "I16X8_LE_U" [macro] rule I16X8_LE_U => b"\xFD\x34"
  syntax Bytes ::= "I16X8_GE_S" [macro] rule I16X8_GE_S => b"\xFD\x35"
  syntax Bytes ::= "I16X8_GE_U" [macro] rule I16X8_GE_U => b"\xFD\x36"

  syntax Bytes ::= "I32X4_EQ" [macro] rule I32X4_EQ => b"\xFD\x37"
  syntax Bytes ::= "I32X4_NE" [macro] rule I32X4_NE => b"\xFD\x38"
  syntax Bytes ::= "I32X4_LT_S" [macro] rule I32X4_LT_S => b"\xFD\x39"
  syntax Bytes ::= "I32X4_LT_U" [macro] rule I32X4_LT_U => b"\xFD\x3A"
  syntax Bytes ::= "I32X4_GT_S" [macro] rule I32X4_GT_S => b"\xFD\x3B"
  syntax Bytes ::= "I32X4_GT_U" [macro] rule I32X4_GT_U => b"\xFD\x3C"
  syntax Bytes ::= "I32X4_LE_S" [macro] rule I32X4_LE_S => b"\xFD\x3D"
  syntax Bytes ::= "I32X4_LE_U" [macro] rule I32X4_LE_U => b"\xFD\x3E"
  syntax Bytes ::= "I32X4_GE_S" [macro] rule I32X4_GE_S => b"\xFD\x3F"
  syntax Bytes ::= "I32X4_GE_U" [macro] rule I32X4_GE_U => b"\xFD\x40"

  syntax Bytes ::= "I64X2_EQ" [macro] rule I64X2_EQ => b"\xFD\xD6\x01"
  syntax Bytes ::= "I64X2_NE" [macro] rule I64X2_NE => b"\xFD\xD7\x01"
  syntax Bytes ::= "I64X2_LT_S" [macro] rule I64X2_LT_S => b"\xFD\xD8\x01"
  syntax Bytes ::= "I64X2_GT_S" [macro] rule I64X2_GT_S => b"\xFD\xD9\x01"
  syntax Bytes ::= "I64X2_LE_S" [macro] rule I64X2_LE_S => b"\xFD\xDA\x01"
  syntax Bytes ::= "I64X2_GE_S" [macro] rule I64X2_GE_S => b"\xFD\xDB\x01"

  syntax Bytes ::= "F32X4_EQ" [macro] rule F32X4_EQ => b"\xFD\x41"
  syntax Bytes ::= "F32X4_NE" [macro] rule F32X4_NE => b"\xFD\x42"
  syntax Bytes ::= "F32X4_LT" [macro] rule F32X4_LT => b"\xFD\x43"
  syntax Bytes ::= "F32X4_GT" [macro] rule F32X4_GT => b"\xFD\x44"
  syntax Bytes ::= "F32X4_LE" [macro] rule F32X4_LE => b"\xFD\x45"
  syntax Bytes ::= "F32X4_GE" [macro] rule F32X4_GE => b"\xFD\x46"

  syntax Bytes ::= "F64X2_EQ" [macro] rule F64X2_EQ => b"\xFD\x47"
  syntax Bytes ::= "F64X2_NE" [macro] rule F64X2_NE => b"\xFD\x48"
  syntax Bytes ::= "F64X2_LT" [macro] rule F64X2_LT => b"\xFD\x49"
  syntax Bytes ::= "F64X2_GT" [macro] rule F64X2_GT => b"\xFD\x4A"
  syntax Bytes ::= "F64X2_LE" [macro] rule F64X2_LE => b"\xFD\x4B"
  syntax Bytes ::= "F64X2_GE" [macro] rule F64X2_GE => b"\xFD\x4C"

  syntax Bytes ::= "V128_NOT" [macro] rule V128_NOT => b"\xFD\x4D"
  syntax Bytes ::= "V128_AND" [macro] rule V128_AND => b"\xFD\x4E"
  syntax Bytes ::= "V128_ANDNOT" [macro] rule V128_ANDNOT => b"\xFD\x4F"
  syntax Bytes ::= "V128_OR" [macro] rule V128_OR => b"\xFD\x50"
  syntax Bytes ::= "V128_XOR" [macro] rule V128_XOR => b"\xFD\x51"
  syntax Bytes ::= "V128_BITSELECT" [macro] rule V128_BITSELECT => b"\xFD\x52"
  syntax Bytes ::= "V128_ANY_TRUE" [macro] rule V128_ANY_TRUE => b"\xFD\x53"

  syntax Bytes ::= "I8X16_ABS" [macro] rule I8X16_ABS => b"\xFD\x60"
  syntax Bytes ::= "I8X16_NEG" [macro] rule I8X16_NEG => b"\xFD\x61"
  syntax Bytes ::= "I8X16_POPCNT" [macro] rule I8X16_POPCNT => b"\xFD\x62"
  syntax Bytes ::= "I8X16_ALL_TRUE" [macro] rule I8X16_ALL_TRUE => b"\xFD\x63"
  syntax Bytes ::= "I8X16_BITMASK" [macro] rule I8X16_BITMASK => b"\xFD\x64"
  syntax Bytes ::= "I8X16_NARROW_I16X8_S" [macro] rule I8X16_NARROW_I16X8_S => b"\xFD\x65"
  syntax Bytes ::= "I8X16_NARROW_I16X8_U" [macro] rule I8X16_NARROW_I16X8_U => b"\xFD\x66"
  syntax Bytes ::= "I8X16_SHL" [macro] rule I8X16_SHL => b"\xFD\x6B"
  syntax Bytes ::= "I8X16_SHR_S" [macro] rule I8X16_SHR_S => b"\xFD\x6C"
  syntax Bytes ::= "I8X16_SHR_U" [macro] rule I8X16_SHR_U => b"\xFD\x6D"
  syntax Bytes ::= "I8X16_ADD" [macro] rule I8X16_ADD => b"\xFD\x6E"
  syntax Bytes ::= "I8X16_ADD_SAT_S" [macro] rule I8X16_ADD_SAT_S => b"\xFD\x6F"
  syntax Bytes ::= "I8X16_ADD_SAT_U" [macro] rule I8X16_ADD_SAT_U => b"\xFD\x70"
  syntax Bytes ::= "I8X16_SUB" [macro] rule I8X16_SUB => b"\xFD\x71"
  syntax Bytes ::= "I8X16_SUB_SAT_S" [macro] rule I8X16_SUB_SAT_S => b"\xFD\x72"
  syntax Bytes ::= "I8X16_SUB_SAT_U" [macro] rule I8X16_SUB_SAT_U => b"\xFD\x73"
  syntax Bytes ::= "I8X16_MIN_S" [macro] rule I8X16_MIN_S => b"\xFD\x76"
  syntax Bytes ::= "I8X16_MIN_U" [macro] rule I8X16_MIN_U => b"\xFD\x77"
  syntax Bytes ::= "I8X16_MAX_S" [macro] rule I8X16_MAX_S => b"\xFD\x78"
  syntax Bytes ::= "I8X16_MAX_U" [macro] rule I8X16_MAX_U => b"\xFD\x79"
  syntax Bytes ::= "I8X16_AVGR_U" [macro] rule I8X16_AVGR_U => b"\xFD\x7B"

  syntax Bytes ::= "I16X8_EXTADD_PAIRWISE_I8X16_S" [macro] rule I16X8_EXTADD_PAIRWISE_I8X16_S => b"\xFD\x7C"
  syntax Bytes ::= "I16X8_EXTADD_PAIRWISE_I8X16_U" [macro] rule I16X8_EXTADD_PAIRWISE_I8X16_U => b"\xFD\x7D"
  syntax Bytes ::= "I16X8_ABS" [macro] rule I16X8_ABS => b"\xFD\x80\x01"
  syntax Bytes ::= "I16X8_NEG" [macro] rule I16X8_NEG => b"\xFD\x81\x01"
  syntax Bytes ::= "I16X8_Q15MULR_SAT_S" [macro] rule I16X8_Q15MULR_SAT_S => b"\xFD\x82\x01"
  syntax Bytes ::= "I16X8_ALL_TRUE" [macro] rule I16X8_ALL_TRUE => b"\xFD\x83\x01"
  syntax Bytes ::= "I16X8_BITMASK" [macro] rule I16X8_BITMASK => b"\xFD\x84\x01"
  syntax Bytes ::= "I16X8_NARROW_I32X4_S" [macro] rule I16X8_NARROW_I32X4_S => b"\xFD\x85\x01"
  syntax Bytes ::= "I16X8_NARROW_I32X4_U" [macro] rule I16X8_NARROW_I32X4_U => b"\xFD\x86\x01"
  syntax Bytes ::= "I16X8_EXTEND_LOW_I8X16_S" [macro] rule I16X8_EXTEND_LOW_I8X16_S => b"\xFD\x87\x01"
  syntax Bytes ::= "I16X8_EXTEND_HIGH_I8X16_S" [macro] rule I16X8_EXTEND_HIGH_I8X16_S => b"\xFD\x88\x01"
  syntax Bytes ::= "I16X8_EXTEND_LOW_I8X16_U" [macro] rule I16X8_EXTEND_LOW_I8X16_U => b"\xFD\x89\x01"
  syntax Bytes ::= "I16X8_EXTEND_HIGH_I8X16_U" [macro] rule I16X8_EXTEND_HIGH_I8X16_U => b"\xFD\x8A\x01"
  syntax Bytes ::= "I16X8_SHL" [macro] rule I16X8_SHL => b"\xFD\x8B\x01"
  syntax Bytes ::= "I16X8_SHR_S" [macro] rule I16X8_SHR_S => b"\xFD\x8C\x01"
  syntax Bytes ::= "I16X8_SHR_U" [macro] rule I16X8_SHR_U => b"\xFD\x8D\x01"
  syntax Bytes ::= "I16X8_ADD" [macro] rule I16X8_ADD => b"\xFD\x8E\x01"
  syntax Bytes ::= "I16X8_ADD_SAT_S" [macro] rule I16X8_ADD_SAT_S => b"\xFD\x8F\x01"
  syntax Bytes ::= "I16X8_ADD_SAT_U" [macro] rule I16X8_ADD_SAT_U => b"\xFD\x90\x01"
  syntax Bytes ::= "I16X8_SUB" [macro] rule I16X8_SUB => b"\xFD\x91\x01"
  syntax Bytes ::= "I16X8_SUB_SAT_S" [macro] rule I16X8_SUB_SAT_S => b"\xFD\x92\x01"
  syntax Bytes ::= "I16X8_SUB_SAT_U" [macro] rule I16X8_SUB_SAT_U => b"\xFD\x93\x01"
  syntax Bytes ::= "I16X8_MUL" [macro] rule I16X8_MUL => b"\xFD\x95\x01"
  syntax Bytes ::= "I16X8_MIN_S" [macro] rule I16X8_MIN_S => b"\xFD\x96\x01"
  syntax Bytes ::= "I16X8_MIN_U" [macro] rule I16X8_MIN_U => b"\xFD\x97\x01"
  syntax Bytes ::= "I16X8_MAX_S" [macro] rule I16X8_MAX_S => b"\xFD\x98\x01"
  syntax Bytes ::= "I16X8_MAX_U" [macro] rule I16X8_MAX_U => b"\xFD\x99\x01"
  syntax Bytes ::= "I16X8_AVGR_U" [macro] rule I16X8_AVGR_U => b"\xFD\x9B\x01"
  syntax Bytes ::= "I16X8_EXTMUL_LOW_I8X16_S" [macro] rule I16X8_EXTMUL_LOW_I8X16_S => b"\xFD\x9C\x01"
  syntax Bytes ::= "I16X8_EXTMUL_HIGH_I8X16_S" [macro] rule I16X8_EXTMUL_HIGH_I8X16_S => b"\xFD\x9D\x01"
  syntax Bytes ::= "I16X8_EXTMUL_LOW_I8X16_U" [macro] rule I16X8_EXTMUL_LOW_I8X16_U => b"\xFD\x9E\x01"
  syntax Bytes ::= "I16X8_EXTMUL_HIGH_I8X16_U" [macro] rule I16X8_EXTMUL_HIGH_I8X16_U => b"\xFD\x9F\x01"

  syntax Bytes ::= "I32X4_EXTADD_PAIRWISE_I16X8_S" [macro] rule I32X4_EXTADD_PAIRWISE_I16X8_S => b"\xFD\x7E"
  syntax Bytes ::= "I32X4_EXTADD_PAIRWISE_I16X8_U" [macro] rule I32X4_EXTADD_PAIRWISE_I16X8_U => b"\xFD\x7F"
  syntax Bytes ::= "I32X4_ABS" [macro] rule I32X4_ABS => b"\xFD\xA0\x01"
  syntax Bytes ::= "I32X4_NEG" [macro] rule I32X4_NEG => b"\xFD\xA1\x01"
  syntax Bytes ::= "I32X4_ALL_TRUE" [macro] rule I32X4_ALL_TRUE => b"\xFD\xA3\x01"
  syntax Bytes ::= "I32X4_BITMASK" [macro] rule I32X4_BITMASK => b"\xFD\xA4\x01"
  syntax Bytes ::= "I32X4_EXTEND_LOW_I16X8_S" [macro] rule I32X4_EXTEND_LOW_I16X8_S => b"\xFD\xA7\x01"
  syntax Bytes ::= "I32X4_EXTEND_HIGH_I16X8_S" [macro] rule I32X4_EXTEND_HIGH_I16X8_S => b"\xFD\xA8\x01"
  syntax Bytes ::= "I32X4_EXTEND_LOW_I16X8_U" [macro] rule I32X4_EXTEND_LOW_I16X8_U => b"\xFD\xA9\x01"
  syntax Bytes ::= "I32X4_EXTEND_HIGH_I16X8_U" [macro] rule I32X4_EXTEND_HIGH_I16X8_U => b"\xFD\xAA\x01"
  syntax Bytes ::= "I32X4_SHL" [macro] rule I32X4_SHL => b"\xFD\xAB\x01"
  syntax Bytes ::= "I32X4_SHR_S" [macro] rule I32X4_SHR_S => b"\xFD\xAC\x01"
  syntax Bytes ::= "I32X4_SHR_U" [macro] rule I32X4_SHR_U => b"\xFD\xAD\x01"
  syntax Bytes ::= "I32X4_ADD" [macro] rule I32X4_ADD => b"\xFD\xAE\x01"
  syntax Bytes ::= "I32X4_SUB" [macro] rule I32X4_SUB => b"\xFD\xB1\x01"
  syntax Bytes ::= "I32X4_MUL" [macro] rule I32X4_MUL => b"\xFD\xB5\x01"
  syntax Bytes ::= "I32X4_MIN_S" [macro] rule I32X4_MIN_S => b"\xFD\xB6\x01"
  syntax Bytes ::= "I32X4_MIN_U" [macro] rule I32X4_MIN_U => b"\xFD\xB7\x01"
  syntax Bytes ::= "I32X4_MAX_S" [macro] rule I32X4_MAX_S => b"\xFD\xB8\x01"
  syntax Bytes ::= "I32X4_MAX_U" [macro] rule I32X4_MAX_U => b"\xFD\xB9\x01"
  syntax Bytes ::= "I32X4_DOT_I16X8_S" [macro] rule I32X4_DOT_I16X8_S => b"\xFD\xBA\x01"
  syntax Bytes ::= "I32X4_EXTMUL_LOW_I16X8_S" [macro] rule I32X4_EXTMUL_LOW_I16X8_S => b"\xFD\xBC\x01"
  syntax Bytes ::= "I32X4_EXTMUL_HIGH_I16X8_S" [macro] rule I32X4_EXTMUL_HIGH_I16X8_S => b"\xFD\xBD\x01"
  syntax Bytes ::= "I32X4_EXTMUL_LOW_I16X8_U" [macro] rule I32X4_EXTMUL_LOW_I16X8_U => b"\xFD\xBE\x01"
  syntax Bytes ::= "I32X4_EXTMUL_HIGH_I16X8_U" [macro] rule I32X4_EXTMUL_HIGH_I16X8_U => b"\xFD\xBF\x01"

  syntax Bytes ::= "I64X2_ABS" [macro] rule I64X2_ABS => b"\xFD\xC0\x01"
  syntax Bytes ::= "I64X2_NEG" [macro] rule I64X2_NEG => b"\xFD\xC1\x01"
  syntax Bytes ::= "I64X2_ALL_TRUE" [macro] rule I64X2_ALL_TRUE => b"\xFD\xC3\x01"
  syntax Bytes ::= "I64X2_BITMASK" [macro] rule I64X2_BITMASK => b"\xFD\xC4\x01"
  syntax Bytes ::= "I64X2_EXTEND_LOW_I32X4_S" [macro] rule I64X2_EXTEND_LOW_I32X4_S => b"\xFD\xC7\x01"
  syntax Bytes ::= "I64X2_EXTEND_HIGH_I32X4_S" [macro] rule I64X2_EXTEND_HIGH_I32X4_S => b"\xFD\xC8\x01"
  syntax Bytes ::= "I64X2_EXTEND_LOW_I32X4_U" [macro] rule I64X2_EXTEND_LOW_I32X4_U => b"\xFD\xC9\x01"
  syntax Bytes ::= "I64X2_EXTEND_HIGH_I32X4_U" [macro] rule I64X2_EXTEND_HIGH_I32X4_U => b"\xFD\xCA\x01"
  syntax Bytes ::= "I64X2_SHL" [macro] rule I64X2_SHL => b"\xFD\xCB\x01"
  syntax Bytes ::= "I64X2_SHR_S" [macro] rule I64X2_SHR_S => b"\xFD\xCC\x01"
  syntax Bytes ::= "I64X2_SHR_U" [macro] rule I64X2_SHR_U => b"\xFD\xCD\x01"
  syntax Bytes ::= "I64X2_ADD" [macro] rule I64X2_ADD => b"\xFD\xCE\x01"
  syntax Bytes ::= "I64X2_SUB" [macro] rule I64X2_SUB => b"\xFD\xD1\x01"
  syntax Bytes ::= "I64X2_MUL" [macro] rule I64X2_MUL => b"\xFD\xD5\x01"
  syntax Bytes ::= "I64X2_EXTMUL_LOW_I32X4_S" [macro] rule I64X2_EXTMUL_LOW_I32X4_S => b"\xFD\xDC\x01"
  syntax Bytes ::= "I64X2_EXTMUL_HIGH_I32X4_S" [macro] rule I64X2_EXTMUL_HIGH_I32X4_S => b"\xFD\xDD\x01"
  syntax Bytes ::= "I64X2_EXTMUL_LOW_I32X4_U" [macro] rule I64X2_EXTMUL_LOW_I32X4_U => b"\xFD\xDE\x01"
  syntax Bytes ::= "I64X2_EXTMUL_HIGH_I32X4_U" [macro] rule I64X2_EXTMUL_HIGH_I32X4_U => b"\xFD\xDF\x01"

  syntax Bytes ::= "F32X4_CEIL" [macro] rule F32X4_CEIL => b"\xFD\x67"
  syntax Bytes ::= "F32X4_FLOOR" [macro] rule F32X4_FLOOR => b"\xFD\x68"
  syntax Bytes ::= "F32X4_TRUNC" [macro] rule F32X4_TRUNC => b"\xFD\x69"
  syntax Bytes ::= "F32X4_NEAREST" [macro] rule F32X4_NEAREST => b"\xFD\x6A"
  syntax Bytes ::= "F32X4_ABS" [macro] rule F32X4_ABS => b"\xFD\xE0\x01"
  syntax Bytes ::= "F32X4_NEG" [macro] rule F32X4_NEG => b"\xFD\xE1\x01"
  syntax Bytes ::= "F32X4_SQRT" [macro] rule F32X4_SQRT => b"\xFD\xE3\x01"
  syntax Bytes ::= "F32X4_ADD" [macro] rule F32X4_ADD => b"\xFD\xE4\x01"
  syntax Bytes ::= "F32X4_SUB" [macro] rule F32X4_SUB => b"\xFD\xE5\x01"
  syntax Bytes ::= "F32X4_MUL" [macro] rule F32X4_MUL => b"\xFD\xE6\x01"
  syntax Bytes ::= "F32X4_DIV" [macro] rule F32X4_DIV => b"\xFD\xE7\x01"
  syntax Bytes ::= "F32X4_MIN" [macro] rule F32X4_MIN => b"\xFD\xE8\x01"
  syntax Bytes ::= "F32X4_MAX" [macro] rule F32X4_MAX => b"\xFD\xE9\x01"
  syntax Bytes ::= "F32X4_PMIN" [macro] rule F32X4_PMIN => b"\xFD\xEA\x01"
  syntax Bytes ::= "F32X4_PMAX" [macro] rule F32X4_PMAX => b"\xFD\xEB\x01"

  syntax Bytes ::= "F64X2_CEIL" [macro] rule F64X2_CEIL => b"\xFD\x74"
  syntax Bytes ::= "F64X2_FLOOR" [macro] rule F64X2_FLOOR => b"\xFD\x75"
  syntax Bytes ::= "F64X2_TRUNC" [macro] rule F64X2_TRUNC => b"\xFD\x7A"
  syntax Bytes ::= "F64X2_NEAREST" [macro] rule F64X2_NEAREST => b"\xFD\x94\x01"
  syntax Bytes ::= "F64X2_ABS" [macro] rule F64X2_ABS => b"\xFD\xEC\x01"
  syntax Bytes ::= "F64X2_NEG" [macro] rule F64X2_NEG => b"\xFD\xED\x01"
  syntax Bytes ::= "F64X2_SQRT" [macro] rule F64X2_SQRT => b"\xFD\xEF\x01"
  syntax Bytes ::= "F64X2_ADD" [macro] rule F64X2_ADD => b"\xFD\xF0\x01"
  syntax Bytes ::= "F64X2_SUB" [macro] rule F64X2_SUB => b"\xFD\xF1\x01"
  syntax Bytes ::= "F64X2_MUL" [macro] rule F64X2_MUL => b"\xFD\xF2\x01"
  syntax Bytes ::= "F64X2_DIV" [macro] rule F64X2_DIV => b"\xFD\xF3\x01"
  syntax Bytes ::= "F64X2_MIN" [macro] rule F64X2_MIN => b"\xFD\xF4\x01"
  syntax Bytes ::= "F64X2_MAX" [macro] rule F64X2_MAX => b"\xFD\xF5\x01"
  syntax Bytes ::= "F64X2_PMIN" [macro] rule F64X2_PMIN => b"\xFD\xF6\x01"
  syntax Bytes ::= "F64X2_PMAX" [macro] rule F64X2_PMAX => b"\xFD\xF7\x01"

  syntax Bytes ::= "I32X4_TRUNC_SAT_F32X4_S" [macro] rule I32X4_TRUNC_SAT_F32X4_S => b"\xFD\xF8\x01"
  syntax Bytes ::= "I32X4_TRUNC_SAT_F32X4_U" [macro] rule I32X4_TRUNC_SAT_F32X4_U => b"\xFD\xF9\x01"
  syntax Bytes ::= "F32X4_CONVERT_I32X4_S" [macro] rule F32X4_CONVERT_I32X4_S => b"\xFD\xFA\x01"
  syntax Bytes ::= "F32X4_CONVERT_I32X4_U" [macro] rule F32X4_CONVERT_I32X4_U => b"\xFD\xFB\x01"
  syntax Bytes ::= "I32X4_TRUNC_SAT_F64X2_S_ZERO" [macro] rule I32X4_TRUNC_SAT_F64X2_S_ZERO => b"\xFD\xFC\x01"
  syntax Bytes ::= "I32X4_TRUNC_SAT_F64X2_U_ZERO" [macro] rule I32X4_TRUNC_SAT_F64X2_U_ZERO => b"\xFD\xFD\x01"
  syntax Bytes ::= "F64X2_CONVERT_LOW_I32X4_S" [macro] rule F64X2_CONVERT_LOW_I32X4_S => b"\xFD\xFE\x01"
  syntax Bytes ::= "F64X2_CONVERT_LOW_I32X4_U" [macro] rule F64X2_CONVERT_LOW_I32X4_U => b"\xFD\xFF\x01"
  syntax Bytes ::= "F32X4_DEMOTE_F64X2_ZERO" [macro] rule F32X4_DEMOTE_F64X2_ZERO => b"\xFD\x5E"
  syntax Bytes ::= "F64X2_PROMOTE_LOW_F32X4" [macro] rule F64X2_PROMOTE_LOW_F32X4 => b"\xFD\x5F"
```

_Expression_ encoding

```k

 syntax Bytes ::= "END" [macro] rule END => b"\x0B"

```

```k
endmodule
```

```k
module BINARY-PARSER //[private]
  imports BINARY-PARSER-BASE
  imports BINARY-PARSER-DATA
  imports BINARY-PARSER-INSTRS
  imports LIST
  imports STRING
  imports WASM

  syntax ModuleOrError ::= ModuleDecl | ParseError

  syntax ModuleOrError ::= parseModule(Bytes)  [function, total]
  rule parseModule(B:Bytes) => checkAllBytesParsed(parseModule(bwi(B, 0)))
  syntax ModuleOrError ::= checkAllBytesParsed(ModuleParseResult)  [function, total]
  rule checkAllBytesParsed(success(M, bwi(B:Bytes, Index:Int))) => M requires Index ==Int lengthBytes(B)
  rule checkAllBytesParsed(E:ParseError) => E

  syntax ModuleParseResult ::= success(ModuleDecl, BytesWithIndex) | ParseError

  syntax ModuleParseResult ::= parseModule(BytesWithIndex)  [function, total]
  rule parseModule(BWI:BytesWithIndex)
      => parseModuleSections(reverseSections(splitSections(parseConstant(parseConstant(BWI, MAGIC), VERSION))))

  syntax ModuleParseResult  ::= parseModuleSections(UnparsedSectionsResult)  [function, total]
                              | #parseModuleSections(ParsedSectionsResult, BytesWithIndex)  [function, total]

  rule parseModuleSections(unparsedSectionsResult(S:UnparsedSections, BWI:BytesWithIndex))
      => #parseModuleSections(parseSections(S), BWI)
  rule parseModuleSections(E:ParseError) => E
  rule #parseModuleSections(S:Sections, BWI:BytesWithIndex)
      => success
          ( addSectionsToModule
              ( S  // Do not reverse, as required by addDefnToModule.
              , moduleAndFunctions
                  ( #module
                      (... types: .Defns
                      , funcs: .Defns
                      , tables: .Defns
                      , mems: .Defns
                      , globals: .Defns
                      , elem: .Defns
                      , data: .Defns
                      , start: .Defns
                      , importDefns: .Defns
                      , exports: .Defns
                      , metadata: #meta(... id: , funcIds: .Map, filename: .String)
                      )
                  , .BinaryDefnFunctionTypes
                  )
              )
          , BWI
          )
  rule #parseModuleSections(E:ParseError, _:BytesWithIndex) => E

  syntax ModuleDecl ::= addSectionsToModule(Sections, ModuleAndFunctions)  [function, total]
  syntax ModuleDecl ::= #addSectionsToModule(Sections, ModuleAndFunctions)  [function, total]
  // TODO: Combine the function types with the function definitions and add them to the module.
  rule addSectionsToModule(.Sections, moduleAndFunctions(M:ModuleDecl, _:BinaryDefnFunctionTypes))
      => M
  rule addSectionsToModule(S:Section : Ss:Sections, M:ModuleAndFunctions)
      => #addSectionsToModule(Ss, addSectionToModule(S, M))
  rule #addSectionsToModule(Ss:Sections, M:ModuleAndFunctions)
      => addSectionsToModule(Ss, M)

  syntax ModuleAndFunctions ::= addSectionToModule(Section, ModuleAndFunctions)  [function, total]
  rule addSectionToModule(customSection(_:Bytes), M:ModuleAndFunctions) => M
  rule addSectionToModule(defnsSection(D:BinaryDefns), M:ModuleAndFunctions)
      => addDefnsToModule(D, M)

  syntax ModuleAndFunctions ::= moduleAndFunctions(mod:ModuleDecl, functionTypes:BinaryDefnFunctionTypes)

  syntax ModuleAndFunctions ::= addDefnsToModule(BinaryDefns, ModuleAndFunctions)  [function, total]
  rule addDefnsToModule(.BinaryDefns, M:ModuleAndFunctions) => M
  rule addDefnsToModule
      ( D:Defn Ds:BinaryDefns => Ds
      , moduleAndFunctions(... mod: M:ModuleDecl => addDefnToModule(false, D, M))
      )
  rule addDefnsToModule
          ( (binaryDefnFunctionType(_TypeIndex:Int) #as FT:BinaryDefnFunctionType) Ds:BinaryDefns
              => Ds
          , moduleAndFunctions(... functionTypes: FTs:BinaryDefnFunctionTypes => FT FTs)
          )

  syntax ModuleDecl ::= addDefnToModule(Bool, Defn, ModuleDecl)  [function, total]
  rule addDefnToModule(true, _, M) => M
  // The following add the defn at the top of the existing defns (e.g. T Ts), so
  // addDefnToModule should be called with Defns in reverse order
  // (the last defn should be processed in the first call).
  rule addDefnToModule(false => true, T:TypeDefn, #module(... types: Ts => T Ts))
  rule addDefnToModule(false => true, I:ImportDefn, #module(... importDefns: Is => I Is))

  syntax Sections ::= List{Section, ":"}
  syntax ParsedSectionsResult ::= Sections | ParseError
  syntax ParsedSectionsResult ::= parseSections(UnparsedSections)  [function, total]
                                | #parseSections(SectionResult, ParsedSectionsResult)  [function, total]
  rule parseSections(.UnparsedSections) => .Sections
  rule parseSections(S:UnparsedSection : Ss:UnparsedSections)
      => #parseSections(parseSection(S), parseSections(Ss))
  rule #parseSections(sectionResult(S:Section, bwi(B:Bytes, I:Int)), Ss:Sections)
      => S : Ss
      requires I ==K lengthBytes(B)
  rule #parseSections(E:ParseError, _) => E
  rule #parseSections(_, E:ParseError) => E
    [owise]

  syntax SectionResult ::= sectionResult(Section, BytesWithIndex) | ParseError
  syntax SectionResult ::= parseSection(UnparsedSection)  [function, total]

  syntax Section ::= customSection(Bytes)
  syntax Section ::= defnsSection(reverseDefns:BinaryDefns)
  rule parseSection(unparsedSection(CUSTOM_SEC, Data:Bytes))
      => sectionResult(customSection(Data), bwi(Data, lengthBytes(Data)))
  rule parseSection(unparsedSection(TYPE_SEC, Data:Bytes))
      => parseTypeSection(bwi(Data, 0))
  rule parseSection(unparsedSection(IMPORT_SEC, Data:Bytes))
      => parseImportSection(bwi(Data, 0))
  rule parseSection(unparsedSection(FUNC_SEC, Data:Bytes))
      => parseFuncSection(bwi(Data, 0))
  rule parseSection(unparsedSection(CODE_SEC, Data:Bytes))
      => parseCodeSection(bwi(Data, 0))
  rule parseSection(A) => parseError("parseSection", ListItem(A))
      [owise]

  syntax SectionResult  ::= parseTypeSection(BytesWithIndex)  [function, total]
                          | #parseTypeSection(IntResult)  [function, total]
  rule parseTypeSection(BWI:BytesWithIndex) => #parseTypeSection(parseLeb128UInt(BWI))
  rule #parseTypeSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnType, Count, .BinaryDefns, BWI)
  rule #parseTypeSection(E:ParseError) => E

  syntax SectionResult  ::= parseImportSection(BytesWithIndex)  [function, total]
                          | #parseImportSection(IntResult)  [function, total]
  rule parseImportSection(BWI:BytesWithIndex) => #parseImportSection(parseLeb128UInt(BWI))
  rule #parseImportSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnImport, Count, .BinaryDefns, BWI)
  rule #parseImportSection(E:ParseError) => E

  syntax SectionResult  ::= parseFuncSection(BytesWithIndex)  [function, total]
                          | #parseFuncSection(IntResult)  [function, total]
  rule parseFuncSection(BWI:BytesWithIndex) => #parseFuncSection(parseLeb128UInt(BWI))
  rule #parseFuncSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnFunc, Count, .BinaryDefns, BWI)
  rule #parseFuncSection(E:ParseError) => E

  syntax SectionResult  ::= parseCodeSection(BytesWithIndex)  [function, total]
                          | #parseCodeSection(IntResult)  [function, total]
  rule parseCodeSection(BWI:BytesWithIndex) => #parseCodeSection(parseLeb128UInt(BWI))
  rule #parseCodeSection(intResult(Count:Int, BWI:BytesWithIndex))
      => parseSectionVector(defnCode, Count, .BinaryDefns, BWI)
  rule #parseCodeSection(E:ParseError) => E

  syntax DefnKind ::= "defnType" | "defnImport" | "defnFunc" | "defnCode"
  syntax SectionResult  ::= parseSectionVector
                                ( type:DefnKind
                                , remainingCount:Int
                                , BinaryDefns
                                , BytesWithIndex
                                )  [function, total]
                          | #parseSectionVector
                                ( type:DefnKind
                                , remainingCount:Int
                                , BinaryDefns
                                , DefnResult
                                )  [function, total]
  rule parseSectionVector(_:DefnKind, 0, D:BinaryDefns, BWI:BytesWithIndex)
      => sectionResult(defnsSection(D), BWI)
  rule parseSectionVector(T:DefnKind, Count:Int, D:BinaryDefns, BWI:BytesWithIndex)
      => #parseSectionVector(T, Count, D, parseDefnType(T, BWI))
      requires Count >Int 0
  rule parseSectionVector(T:DefnKind, Count:Int, D:BinaryDefns, bwi(B:Bytes, I:Int))
      => parseError("parseSectionVector", ListItem(T) ListItem(Count) ListItem(D) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseSectionVector
          ( T:DefnKind
          , RemainingCount:Int
          , Ds:BinaryDefns
          , defnResult(D:BinaryDefn, BWI:BytesWithIndex)
          )
      => parseSectionVector(T, RemainingCount -Int 1, D Ds, BWI)
  rule #parseSectionVector(_:DefnKind, _RemainingCount:Int, _Ds:BinaryDefns, E:ParseError)
      => E

  syntax DefnResult ::= parseDefnType(DefnKind, BytesWithIndex)  [function, total]
  rule parseDefnType(defnType, BWI:BytesWithIndex) => parseDefnType(BWI)
  rule parseDefnType(defnImport, BWI:BytesWithIndex) => parseDefnImport(BWI)
  rule parseDefnType(defnFunc, BWI:BytesWithIndex) => parseDefnFunc(BWI)
  rule parseDefnType(defnCode, BWI:BytesWithIndex) => parseDefnCode(BWI)

  syntax BinaryDefns ::= List{BinaryDefn, ""}
  syntax BinaryDefnFunctionTypes ::= List{BinaryDefnFunctionType, ""}

  syntax BinaryDefnFunctionType ::= binaryDefnFunctionType(typeIndex: Int)
  syntax BinaryDefn ::= Defn
                      | BinaryDefnFunctionType
  syntax DefnResult ::= defnResult(BinaryDefn, BytesWithIndex) | ParseError

  syntax DefnResult ::= parseDefnType(BytesWithIndex)  [function, total]
                      | #parseDefnType(BytesWithIndexOrError)  [function, total]
                      | #parseDefnType1(ResultTypeResult)  [function, total]
                      | #parseDefnType2(VecType, ResultTypeResult)  [function, total]
  rule parseDefnType(BWI:BytesWithIndex) => #parseDefnType(parseConstant(BWI, TYPE_FUN))
  rule #parseDefnType(BWI:BytesWithIndex) => #parseDefnType1(parseResultType(BWI))
  rule #parseDefnType(E:ParseError) => E
  rule #parseDefnType1(resultTypeResult(V:VecType, BWI:BytesWithIndex))
      => #parseDefnType2(V, parseResultType(BWI))
  rule #parseDefnType1(E:ParseError) => E
  rule #parseDefnType2(V1:VecType, resultTypeResult(V2:VecType, BWI:BytesWithIndex))
      => defnResult(#type(V1 -> V2, ), BWI:BytesWithIndex)
  rule #parseDefnType2(_:VecType, E:ParseError) => E

  syntax ResultTypeResult ::= resultTypeResult(VecType, BytesWithIndex) | ParseError
  syntax ResultTypeResult ::= parseResultType(BytesWithIndex)  [function, total]
                            | #parseResultType(IntResult)  [function, total]
                            | #parseResultType1(ValTypesResult)  [function, total]
  rule parseResultType(BWI:BytesWithIndex) => #parseResultType(parseLeb128UInt(BWI))
  rule #parseResultType(intResult(Count:Int, BWI:BytesWithIndex))
      => #parseResultType1(parseValTypes(Count, .ValTypes, BWI))
  rule #parseResultType(E:ParseError) => E
  rule #parseResultType1(valTypesResult(V:ValTypes, BWI:BytesWithIndex))
      => resultTypeResult([V], BWI)
  rule #parseResultType1(E:ParseError) => E

  syntax ValTypesResult ::= valTypesResult(ValTypes, BytesWithIndex) | ParseError
  syntax ValTypesResult ::= parseValTypes(remaining:Int, ValTypes, BytesWithIndex)  [function, total]
                          | #parseValTypes(remaining:Int, ValTypes, ValTypeResult)  [function, total]
  rule parseValTypes(0, V:ValTypes, BWI:BytesWithIndex)
      => valTypesResult(reverse(V), BWI)
  rule parseValTypes(Count:Int, V:ValTypes, BWI:BytesWithIndex)
      => #parseValTypes(Count -Int 1, V, parseValType(BWI))
      requires Count >Int 0
  rule parseValTypes(Count:Int, V:ValTypes, bwi(B:Bytes, I:Int))
      => parseError("parseValTypes", ListItem(Count) ListItem(V) ListItem(I) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseValTypes(Count:Int, Vs:ValTypes, valTypeResult(V:ValType, BWI:BytesWithIndex))
      => parseValTypes(Count, V Vs, BWI)
  rule #parseValTypes(_:Int, _:ValTypes, E:ParseError) => E

  syntax ValTypes ::= reverse(ValTypes)  [function, total]
                    | #reverse(ValTypes, ValTypes)  [function, total]
  rule reverse(V:ValTypes) => #reverse(V, .ValTypes)
  rule #reverse(.ValTypes, Vs:ValTypes) => Vs
  rule #reverse(V:ValType Vs1:ValTypes, Vs2:ValTypes) => #reverse(Vs1, V Vs2)

  syntax DefnResult ::= parseDefnImport(BytesWithIndex)  [function, total]
                      | #parseDefnImport1(NameResult)  [function, total]
                      | #parseDefnImport2(WasmString, NameResult)  [function, total]
                      | #parseDefnImport3(WasmString, WasmString, ImportDescResult)  [function, total]
  rule parseDefnImport(BWI:BytesWithIndex) => #parseDefnImport1(parseName(BWI))
  rule #parseDefnImport1(nameResult(Name:WasmString, BWI:BytesWithIndex))
      => #parseDefnImport2(Name, parseName(BWI))
  rule #parseDefnImport1(E:ParseError) => E
  rule #parseDefnImport2(ModuleName:WasmString, nameResult(ObjectName:WasmString, BWI:BytesWithIndex))
      => #parseDefnImport3(ModuleName, ObjectName, parseImportDesc(BWI))
  rule #parseDefnImport2(_, E:ParseError) => E
  rule #parseDefnImport3(ModuleName:WasmString, ObjectName:WasmString, importDescResult(Desc:ImportDesc, BWI:BytesWithIndex))
      => defnResult(#import(ModuleName, ObjectName, Desc), BWI)
  rule #parseDefnImport3(_, _, E:ParseError) => E


  syntax ImportDescResult ::= importDescResult(ImportDesc, BytesWithIndex) | ParseError
  syntax ImportDescResult ::= parseImportDesc(BytesWithIndex)  [function, total]
                            | #parseImportDescFunc(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescTable(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescMem(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | #parseImportDescGlobal(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                            | parseImportDescFunc(IntResult)  [function, total]
                            | parseImportDescTable(ValTypeResult)  [function, total]
                            | #parseImportDescTable1(ValType, LimitsResult)  [function, total]
                            | parseImportDescMem(LimitsResult)  [function, total]
                            | parseImportDescGlobal(ValTypeResult)  [function, total]
                            | #parseImportDescGlobal1(ValType, MutResult)  [function, total]
  rule parseImportDesc(BWI:BytesWithIndex)
      => #parseImportDescFunc(BWI, parseConstant(BWI, IMPORT_FUNC))
  rule #parseImportDescFunc(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescFunc(parseLeb128UInt(BWI))
  rule #parseImportDescFunc(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescTable(BWI, parseConstant(BWI, IMPORT_TBLT))
  rule #parseImportDescTable(_:BytesWithIndex, BWI:BytesWithIndex)
      // TODO: This should use parseRefType in order to properly validate the
      // data, but we are dropping the result for now so we're using the
      // already implemented parseValType.
      => parseImportDescTable(parseValType(BWI))
  rule #parseImportDescTable(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescMem(BWI, parseConstant(BWI, IMPORT_MEMT))
  rule #parseImportDescMem(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescMem(parseLimits(BWI))
  rule #parseImportDescMem(BWI:BytesWithIndex, _:ParseError)
      => #parseImportDescGlobal(BWI, parseConstant(BWI, IMPORT_GLBT))
  rule #parseImportDescGlobal(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseImportDescGlobal(parseValType(BWI))
  rule #parseImportDescGlobal(_:BytesWithIndex, E:ParseError) => E

  rule parseImportDescFunc(intResult(Value:Int, BWI:BytesWithIndex))
      => importDescResult(#funcDesc(, Value), BWI)
  rule parseImportDescFunc(E:ParseError) => E

  rule parseImportDescTable(valTypeResult(Value:ValType, BWI:BytesWithIndex))
      => #parseImportDescTable1(Value, parseLimits(BWI))
  rule parseImportDescTable(E:ParseError) => E
  // TODO: Do we need RefType for anything?
  rule #parseImportDescTable1(_RefType:ValType, limitsResult(L:Limits, BWI:BytesWithIndex))
      => importDescResult(#tableDesc(, L), BWI)
  rule #parseImportDescTable1(_, E:ParseError) => E

  rule parseImportDescMem(limitsResult(L:Limits, BWI:BytesWithIndex))
      => importDescResult(#memoryDesc(, L), BWI)
  rule parseImportDescMem(E:ParseError) => E

  rule parseImportDescGlobal(valTypeResult(T:ValType, BWI:BytesWithIndex))
      => #parseImportDescGlobal1(T, parseMut(BWI))
  rule parseImportDescGlobal(E:ParseError) => E
  rule #parseImportDescGlobal1(T:ValType, mutResult(Mut:Mut, BWI:BytesWithIndex))
      => importDescResult(#globalDesc(, Mut T), BWI)
  rule #parseImportDescGlobal1(_, E:ParseError) => E


  syntax DefnResult ::= parseDefnFunc(BytesWithIndex)  [function, total]
                      | #parseDefnFunc(IntResult)  [function, total]
  rule parseDefnFunc(BWI:BytesWithIndex) => #parseDefnFunc(parseLeb128UInt(BWI))
  rule #parseDefnFunc(intResult(TypeIndex:Int, BWI:BytesWithIndex))
      => defnResult(binaryDefnFunctionType(TypeIndex), BWI)
  rule #parseDefnFunc(E:ParseError) => E


  syntax DefnResult ::= parseDefnCode(BytesWithIndex)  [function, total]
                      | #parseDefnCode(sizeInBytes:IntResult)  [function, total]
                      | #parseDefnCode1(sizeInBytes:Int, ValTypesResult)  [function, total]
                      | #parseDefnCode2(sizeInBytes:Int, ValTypes, InstrListResult)  [function, total]
  rule parseDefnCode(BWI:BytesWithIndex) => #parseDefnCode(parseLeb128UInt(BWI))
  rule #parseDefnCode(intResult(Size:Int, BWI:BytesWithIndex))
      => #parseDefnCode1(Size, parseLocalsVec(BWI))
  rule #parseDefnCode(E:ParseError) => E
      => defnResult(binaryDefnFunctionType(Size), BWI)
  rule #parseDefnCode1(Size:Int, valTypesResult(Locals:ValTypes, BWI:BytesWithIndex))
      => #parseDefnCode2(Size, Locals, parseInstrList(BWI))
  rule #parseDefnCode1(_, E:ParseError) => E
  rule #parseDefnCode2(_Size:Int, Locals:ValTypes, instrListResult(Is:Instrs, BWI:BytesWithIndex))
      => defnResult(binaryDefnFunction([ Locals ], Is), BWI)
  rule #parseDefnCode2(_, _, E:ParseError) => E


  syntax InstrListResult ::= instrListResult(Instrs, BytesWithIndex) | ParseError

  syntax InstrListResult  ::= parseInstrList(BytesWithIndex, Instrs) [function, total]
                            | #parseInstrList1(BytesWithIndex, BytesWithIndexOrError) [function, total]
                            | #parseInstrList2(BytesWithIndex, InstrResult) [function, total]
  rule parseInstrList(BWI:BytesWithIndex, Is:Instrs) => #parseInstrList1(BWI, parseConstant(BWI, END), Is)
  rule #parseInstrList1(_:BytesWithIndex, BWI:BytesWithIndex, Is:Instrs)
      => instrListResult(reverse(Is), BWI)
  rule #parseInstrList1(BWI:BytesWithIndex, _:ParseError, Is:Instrs)
      => #parseInstrList2(BWI, parseInstr(BWI), Is)
  rule #parseInstrList2(BWI:BytesWithIndex, instrResult(I:Instr, BWI:BytesWithIndex), Is:Instrs)
      => parseInstrList(BWI, I Is)
  rule #parseInstrList2(_, E:ParseError, _) => E

  syntax MutResult ::= mutResult(Mut, BytesWithIndex) | ParseError
  syntax MutResult ::= parseMut(BytesWithIndex)  [function, total]
                      | #parseMut1(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                      | #parseMut2(BytesWithIndexOrError)  [function, total]
  rule parseMut(BWI:BytesWithIndex) => #parseMut1(BWI, parseConstant(BWI, GLOBAL_CNST))
  rule #parseMut1(_:BytesWithIndex, BWI:BytesWithIndex) => mutResult(const, BWI)
  rule #parseMut1(BWI, _:ParseError) => #parseMut2(parseConstant(BWI, GLOBAL_VAR))
  rule #parseMut2(BWI:BytesWithIndex) => mutResult(var, BWI)
  rule #parseMut2(E:ParseError) => E

  syntax LimitsResult ::= limitsResult(Limits, BytesWithIndex) | ParseError
  syntax LimitsResult ::= parseLimits(BytesWithIndex)  [function, total]
                        | #parseLimits1(BytesWithIndex, BytesWithIndexOrError)  [function, total]
                        | #parseLimits2(BytesWithIndexOrError)  [function, total]
                        | parseLimitsMin(IntResult)  [function, total]
                        | parseLimitsMinMax(IntResult)  [function, total]
                        | #parseLimitsMinMax(Int, IntResult)  [function, total]
  rule parseLimits(BWI:BytesWithIndex) => #parseLimits1(BWI, parseConstant(BWI, LIMITS_MIN))
  rule #parseLimits1(_:BytesWithIndex, BWI:BytesWithIndex)
      => parseLimitsMin(parseLeb128UInt(BWI))
  rule #parseLimits1(BWI:BytesWithIndex, _:ParseError)
      => #parseLimits2(parseConstant(BWI, LIMITS))
  rule #parseLimits2(BWI:BytesWithIndex)
      => parseLimitsMinMax(parseLeb128UInt(BWI))
  rule #parseLimits2(E:ParseError) => E

  rule parseLimitsMin(intResult(Min:Int, BWI:BytesWithIndex))
      => limitsResult(#limitsMin(Min), BWI)
  rule parseLimitsMin(E:ParseError) => E

  rule parseLimitsMinMax(intResult(Min:Int, BWI:BytesWithIndex))
      => #parseLimitsMinMax(Min, parseLeb128UInt(BWI))
  rule parseLimitsMinMax(E:ParseError) => E
  rule #parseLimitsMinMax(Min:Int, intResult(Max:Int, BWI:BytesWithIndex))
      => limitsResult(#limits(Min, Max), BWI)
  rule #parseLimitsMinMax(_, E:ParseError) => E


  syntax NameResult ::= nameResult(WasmString, BytesWithIndex) | ParseError
  syntax NameResult ::= parseName(BytesWithIndex)  [function, total]
                      | #parseName(IntResult)  [function, total]
  rule parseName(BWI:BytesWithIndex) => #parseName(parseLeb128UInt(BWI))
  rule #parseName(intResult(Length:Int, bwi(B:Bytes, Index:Int)))
      // TODO: This should be decoded as an UTF-8 string. However, we do not have
      // a good option when doing concrete execution. The documentation for
      // Bytes2String does not specify an encoding, and decodeBytes is a partial
      // function in a symbolic module.
      => nameResult
          ( #String2WasmString(Bytes2String(substrBytes(B, Index, Index +Int Length)))
          , bwi(B, Index +Int Length)
          )
      requires 0 <=Int Index andBool Index +Int Length <=Int lengthBytes(B)
  rule #parseName(intResult(Length:Int, bwi(B:Bytes, Index:Int)))
      => parseError("#parseName", ListItem(Length) ListItem(Index) ListItem(lengthBytes(B)) ListItem(B))
      [owise]
  rule #parseName(E:ParseError) => E

  syntax UnparsedSection ::= unparsedSection(sectionId:Int, sectionData:Bytes)
  syntax UnparsedSectionResult ::= unparsedSectionResult(UnparsedSection, BytesWithIndex) | ParseError
  syntax UnparsedSectionResult  ::= splitSection(BytesWithIndex) [function, total]
                                  | #splitSection(sectionId:Int, IntResult) [function, total]

  rule splitSection(bwi(Buffer:Bytes, Index:Int))
      => #splitSection(Buffer[Index], parseLeb128UInt(bwi(Buffer, Index +Int 1)))
      requires Index <Int lengthBytes(Buffer)

  rule #splitSection(SectionId, intResult(SectionLength:Int, bwi(Buffer:Bytes, Index:Int)))
      => unparsedSectionResult
          ( unparsedSection(SectionId, substrBytes(Buffer, Index, Index +Int SectionLength))
          , bwi(Buffer, Index +Int SectionLength)
          )
      requires 0 <=Int Index andBool Index +Int SectionLength <=Int lengthBytes(Buffer)
  rule #splitSection(SectionId:Int, intResult(SectionLength:Int, bwi(Buffer:Bytes, Index:Int)))
      => parseError("splitSection", ListItem(SectionId) ListItem(SectionLength) ListItem(Index) ListItem(lengthBytes(Buffer)) ListItem(Buffer))
      [owise]
  rule #splitSection(_SectionId:Int, E:ParseError) => E


  syntax UnparsedSections ::= List{UnparsedSection, ":"}
  syntax UnparsedSectionsResult ::= unparsedSectionsResult(UnparsedSections, BytesWithIndex) | ParseError

  syntax UnparsedSections ::= reverse(UnparsedSections)  [function, total]
                            | #reverse(UnparsedSections, UnparsedSections)  [function, total]
  rule reverse(S:UnparsedSections) => #reverse(S, .UnparsedSections)
  rule #reverse(.UnparsedSections, S:UnparsedSections) => S
  rule #reverse(S:UnparsedSection : Ss1:UnparsedSections, Ss2:UnparsedSections) => #reverse(Ss1, S: Ss2)

  syntax UnparsedSectionsResult ::= reverseSections(UnparsedSectionsResult)  [function, total]
  rule reverseSections(unparsedSectionsResult(S:UnparsedSections, BWI:BytesWithIndex))
      => unparsedSectionsResult(reverse(S), BWI)
  rule reverseSections(E:ParseError) => E

  syntax UnparsedSectionsResult ::= splitSections(BytesWithIndexOrError)  [function, total]
                                  | #splitSections(UnparsedSectionResult)  [function, total]
                                  | concatOrError(UnparsedSection, UnparsedSectionsResult)  [function, total]

  rule splitSections(bwi(B:Bytes, Index:Int))
      => unparsedSectionsResult(.UnparsedSections, bwi(B:Bytes, Index:Int))
      requires Index ==K lengthBytes(B)
  rule splitSections(BWI:BytesWithIndex)
      => #splitSections(splitSection(BWI))
      [owise]
  rule splitSections(E:ParseError) => E

  rule #splitSections(unparsedSectionResult(S:UnparsedSection, BWI:BytesWithIndex))
      => concatOrError(S, splitSections(BWI))
  rule #splitSections(E:ParseError) => E

  rule concatOrError(S:UnparsedSection, unparsedSectionsResult(Ss:UnparsedSections, BWI:BytesWithIndex))
      => unparsedSectionsResult(S : Ss, BWI)
  rule concatOrError(_:UnparsedSection, E:ParseError) => E

endmodule
```
