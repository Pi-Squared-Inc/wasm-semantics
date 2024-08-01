Numeric Instructions
--------------------

In this file we implement the numeric rules specified in section `4.3 Numerics` of the offical WebAssembly specification.

In the notations of some operators, `sx` is the signedness of the operator and could be either `s` (signed) or `u` (unsigned), which indicates whether the operands should be interpreted as signed integer or unsigned integer.

```k
requires "data.md"

module WASM-NUMERIC-SYNTAX

    syntax IUnOp ::= "clz"    [symbol(aClz)]
                   | "ctz"    [symbol(aCtz)]
                   | "popcnt" [symbol(aPopcnt)]
 // ---------------------------------------------------

    syntax FUnOp ::= "abs"     [symbol(aAbs)]
                   | "neg"     [symbol(aNeg)]
                   | "sqrt"    [symbol(aSqrt)]
                   | "floor"   [symbol(aFloor)]
                   | "ceil"    [symbol(aCeil)]
                   | "trunc"   [symbol(aTrunc)]
                   | "nearest" [symbol(aNearest)]
 // -----------------------------------------------------

    syntax ExtendS ::= "extend8_s"   [symbol(aExtend8_s)]
                     | "extend16_s"  [symbol(aExtend16_s)]
                     | "extend32_s"  [symbol(aExtend32_s)]
 // ---------------------------------------------------------------

    syntax IBinOp ::= "add" [symbol(intAdd)]
                    | "sub" [symbol(intSub)]
                    | "mul" [symbol(intMul)]
                    | "div_u" [symbol(intDiv_u)]
                    | "rem_u" [symbol(intRem_u)]
                    | "div_s" [symbol(intDiv_s)]
                    | "rem_s" [symbol(intRem_s)]
                    | "and" [symbol(intAnd)]
                    | "or" [symbol(intOr)]
                    | "xor" [symbol(intXor)]
                    | "shl" [symbol(intShl)]
                    | "shr_u" [symbol(intShr_u)]
                    | "shr_s" [symbol(intShr_s)]
                    | "rotl" [symbol(intRotl)]
                    | "rotr" [symbol(intRotr)]
 // --------------------------------------------------

    syntax FBinOp ::= "add" [symbol(floatAdd)]
                    | "sub" [symbol(floatSub)]
                    | "mul" [symbol(floatMul)]
                    | "div" [symbol(floatDiv)]
                    | "min" [symbol(floatMin)]
                    | "max" [symbol(floatMax)]
                    | "copysign" [symbol(floatCopysign)]
 // ------------------------------------------------------------

    syntax TestOp ::= "eqz" [symbol(aEqz)]
 // ----------------------------------------------

    syntax IRelOp ::= "eq" [symbol(intEq)]
                    | "ne" [symbol(intNe)]
                    | "lt_u" [symbol(intLt_u)]
                    | "gt_u" [symbol(intGt_u)]
                    | "lt_s" [symbol(intLt_s)]
                    | "gt_s" [symbol(intGt_s)]
                    | "le_u" [symbol(intLe_u)]
                    | "ge_u" [symbol(intGe_u)]
                    | "le_s" [symbol(intLe_s)]
                    | "ge_s" [symbol(intGe_s)]
 // --------------------------------------------------

    syntax FRelOp ::= "lt" [symbol(floatLt)]
                    | "gt" [symbol(floatGt)]
                    | "le" [symbol(floatLe)]
                    | "ge" [symbol(floatGe)]
                    | "eq" [symbol(floatEq)]
                    | "ne" [symbol(floatNe)]
 // ------------------------------------------------

    syntax CvtOp ::= Cvti32Op | Cvti64Op | Cvtf32Op | Cvtf64Op
 // ----------------------------------------------------------

    syntax Cvti32Op ::= "extend_i32_u" [symbol(aExtend_i32_u)]
                      | "extend_i32_s" [symbol(aExtend_i32_s)]
                      | "convert_i32_s" [symbol(aConvert_i32_s)]
                      | "convert_i32_u" [symbol(aConvert_i32_u)]
 // --------------------------------------------------------------------

    syntax Cvti64Op ::= "wrap_i64" [symbol(aWrap_i64)]
                      | "convert_i64_s" [symbol(aConvert_i64_s)]
                      | "convert_i64_u" [symbol(aConvert_i64_u)]
 // --------------------------------------------------------------------

    syntax Cvtf32Op ::= "promote_f32" [symbol(aPromote_f32)]
                      | "trunc_f32_s" [symbol(aTrunc_f32_s)]
                      | "trunc_f32_u" [symbol(aTrunc_f32_u)]
 // ----------------------------------------------------------------

    syntax Cvtf64Op ::= "demote_f64" [symbol(aDemote_f64)]
                      | "trunc_f64_s" [symbol(aTrunc_f64_s)]
                      | "trunc_f64_u" [symbol(aTrunc_f64_u)]
 // ----------------------------------------------------------------

endmodule

module WASM-NUMERIC
    imports WASM-NUMERIC-SYNTAX
    imports WASM-DATA

```

### Unary Operators

`*UnOp` takes one oprand and returns a `Val`.

```k
    syntax Val ::= I32ValType "." IUnOp   MInt{32}   [symbol(int32UnOp)    , function, total]
                 | I64ValType "." IUnOp   MInt{64}   [symbol(int64UnOp)    , function, total]
                 | FValType   "." FUnOp   Float      [symbol(floatUnOp)    , function]
                 | I32ValType "." ExtendS MInt{32}   [symbol(extendS32UnOp), function, total]
                 | I64ValType "." ExtendS MInt{64}   [symbol(extendS64UnOp), function, total]
 // --------------------------------------------------------------------------------------------
```

#### Unary Operators for Integers

There three unary operators for integers: `clz`, `ctz` and `popcnt`.

- `clz` counts the number of leading zero-bits, with 0 having all leading zero-bits.
- `ctz` counts the number of trailing zero-bits, with 0 having all trailing zero-bits.
- `popcnt` counts the number of non-zero bits.

Note: The actual `ctz` operator considers the integer 0 to have *all* zero-bits, whereas the `#ctz` helper function considers it to have *no* zero-bits, in order for it to be width-agnostic.

```k
    rule ITYPE:I32ValType . clz    I1 => < ITYPE > roundMInt(#width(ITYPE)) -MInt #minWidth(I1)
    rule ITYPE:I64ValType . clz    I1 => < ITYPE > #width(ITYPE) -MInt #minWidth(I1)
    rule ITYPE:I32ValType . ctz    I1 => < ITYPE > #if I1 ==MInt 0p32 #then roundMInt(#width(ITYPE)) #else #ctz(I1) #fi
    rule ITYPE:I64ValType . ctz    I1 => < ITYPE > #if I1 ==MInt 0p64 #then #width(ITYPE) #else #ctz(I1) #fi
    rule ITYPE:I32ValType . popcnt I1 => < ITYPE > #popcnt(I1)
    rule ITYPE:I64ValType . popcnt I1 => < ITYPE > #popcnt(I1)

    syntax MInt{32} ::= #minWidth ( MInt{32} ) [function, total]
                      | #ctz      ( MInt{32} ) [function, total]
                      | #popcnt   ( MInt{32} ) [function, total]
    syntax MInt{64} ::= #minWidth ( MInt{64} ) [function, total, symbol(minWidth64)]
                      | #ctz      ( MInt{64} ) [function, total, symbol(ctz64)]
                      | #popcnt   ( MInt{64} ) [function, total, symbol(popcnt64)]
 // ------------------------------------------------------------
    rule #minWidth(N) => 0p32                                                        requires N ==MInt 0p32
    rule #minWidth(N) => 0p64                                                        requires N ==MInt 0p64
    rule #minWidth(N) => 1p32 +MInt #minWidth(N >>lMInt 1p32)                        requires N =/=MInt 0p32
    rule #minWidth(N) => 1p64 +MInt #minWidth(N >>lMInt 1p64)                        requires N =/=MInt 0p64

    rule #ctz(N) => 0p32                                                             requires N ==MInt 0p32
    rule #ctz(N) => 0p64                                                             requires N ==MInt 0p64
    rule #ctz(N) => 0p32                                                             requires N =/=MInt 0p32 andBool N &MInt 1p32 ==MInt 1p32
    rule #ctz(N) => 0p64                                                             requires N =/=MInt 0p64 andBool N &MInt 1p64 ==MInt 1p64
    rule #ctz(N) => 1p32 +MInt #ctz(N >>lMInt 1p32)                                  [owise]
    rule #ctz(N) => 1p64 +MInt #ctz(N >>lMInt 1p64)                                  [owise]

    rule #popcnt(N) => 0p32                                                          requires N ==MInt 0p32
    rule #popcnt(N) => 0p64                                                          requires N ==MInt 0p64
    rule #popcnt(N) => #bool(N &MInt 1p32 ==MInt 1p32) +MInt #popcnt(N >>lMInt 1p32) requires N =/=MInt 0p32
    rule #popcnt(N) => roundMInt(#bool(N &MInt 1p64 ==MInt 1p64)) +MInt #popcnt(N >>lMInt 1p64) requires N =/=MInt 0p64
```

Before we implement the rule for float point numbers, we first need to define a helper function.

- `#isInfinityOrNaN` judges whether a `float` is infinity or NaN.

```k
    syntax Bool ::= #isInfinityOrNaN ( Float ) [function]
 // -----------------------------------------------------
    rule #isInfinityOrNaN ( F ) => (isNaN(F) orBool isInfinite(F))
```

#### Unary Operators for Floats

There are 7 unary operators for floats: `abs`, `neg`, `sqrt`, `floor`, `ceil`, `trunc` and `nearest`.

- `abs` returns the absolute value of the given float point number.
- `neg` returns the additive inverse value of the given float point number.
- `sqrt` returns the square root of the given float point number.
- `floor` returns the greatest integer less than or equal to the given float point number.
- `ceil` returns the least integer greater than or equal to the given float point number.
- `trunc` returns the integral value by discarding the fractional part of the given float.
- `nearest` returns the integral value that is nearest to the given float number; if two values are equally near, returns the even one.

```k
    rule FTYPE . abs     F => < FTYPE >   absFloat (F)
    rule FTYPE . neg     F => < FTYPE >    --Float  F
    rule FTYPE . sqrt    F => < FTYPE >  sqrtFloat (F)
    rule FTYPE . floor   F => < FTYPE > floorFloat (F)
    rule FTYPE . ceil    F => < FTYPE >  ceilFloat (F)
    rule FTYPE . trunc   F => < FTYPE > truncFloat (F)
    rule FTYPE . nearest F => < FTYPE >  F                requires          #isInfinityOrNaN (F)
    rule FTYPE . nearest F => #round(FTYPE, Float2Int(F)) requires (notBool #isInfinityOrNaN (F)) andBool notBool (Float2Int(F) ==Int 0 andBool signFloat(F))
    rule FTYPE . nearest F => < FTYPE > -0.0              requires (notBool #isInfinityOrNaN (F)) andBool          Float2Int(F) ==Int 0 andBool signFloat(F)
```

#### Sign-extension Operators for Integers

There are 3 sign-extension operators for integers.

- `extend8_s`
- `extend16_s`
- `extend32_s`

```k
    rule ITYPE:I32ValType . extend8_s  I  => < ITYPE > signExtendMInt(roundMInt(I)::MInt{8})
    rule ITYPE:I64ValType . extend8_s  I  => < ITYPE > signExtendMInt(roundMInt(I)::MInt{8})
    rule ITYPE:I32ValType . extend16_s I  => < ITYPE > signExtendMInt(roundMInt(I)::MInt{16})
    rule ITYPE:I64ValType . extend16_s I  => < ITYPE > signExtendMInt(roundMInt(I)::MInt{16})
    rule     _:I32ValType . extend32_s _I => undefined
    rule ITYPE:I64ValType . extend32_s I  => < ITYPE > signExtendMInt(roundMInt(I)::MInt{32})
```

### Binary Operators

`*BinOp` takes two oprands and returns a `Val`.
A `*BinOp` operator always produces a result of the same type as its operands.

```k
    syntax Val ::= I32ValType "." IBinOp MInt{32}   MInt{32}   [symbol(int32BinOp), function, total]
                 | I64ValType "." IBinOp MInt{64}   MInt{64}   [symbol(int64BinOp), function, total]
                 | FValType "." FBinOp Float Float [symbol(floatBinOp), function]
 // -----------------------------------------------------------------------------
```

Make intBinOp total

```k

rule _:I32ValType . _:IBinOp _:MInt{32} _:MInt{32} => undefined [owise]
rule _:I64ValType . _:IBinOp _:MInt{64} _:MInt{64} => undefined [owise]

```

#### Binary Operators for Integers

There are 12 binary operators for integers: `add`, `sub`, `mul`, `div_sx`, `rem_sx`, `and`, `or`, `xor`, `shl`, `shr_sx`, `rotl`, `rotr`.


- `add` returns the result of adding up the 2 given integers modulo 2^N.
- `sub` returns the result of substracting the second oprand from the first oprand modulo 2^N.
- `mul` returns the result of multiplying the 2 given integers modulo 2^N.

`add`, `sub`, and `mul` are given semantics by lifting the correct K operators through the `#chop` function.

```k
    rule ITYPE:I32ValType . add I1 I2 => < ITYPE > I1 +MInt I2
    rule ITYPE:I32ValType . sub I1 I2 => < ITYPE > I1 -MInt I2
    rule ITYPE:I32ValType . mul I1 I2 => < ITYPE > I1 *MInt I2
    rule ITYPE:I64ValType . add I1 I2 => < ITYPE > I1 +MInt I2
    rule ITYPE:I64ValType . sub I1 I2 => < ITYPE > I1 -MInt I2
    rule ITYPE:I64ValType . mul I1 I2 => < ITYPE > I1 *MInt I2
```

- `div_sx` returns the result of dividing the first operand by the second oprand, truncated toward zero.
- `rem_sx` returns the remainder of dividing the first operand by the second oprand.

`div_sx` and `rem_sx` have extra side-conditions about when they are defined or not.

```k
    rule  ITYPE:I32ValType . div_u  I1 I2 => < ITYPE > I1 /uMInt I2 requires I2 =/=MInt 0p32
    rule  ITYPE:I64ValType . div_u  I1 I2 => < ITYPE > I1 /uMInt I2 requires I2 =/=MInt 0p64
    rule _ITYPE:I32ValType . div_u _I1 I2 => undefined            requires I2  ==MInt 0p32
    rule _ITYPE:I64ValType . div_u _I1 I2 => undefined            requires I2  ==MInt 0p64

    rule  ITYPE:I32ValType . rem_u  I1 I2 => < ITYPE > I1 %uMInt I2 requires I2 =/=MInt 0p32
    rule  ITYPE:I64ValType . rem_u  I1 I2 => < ITYPE > I1 %uMInt I2 requires I2 =/=MInt 0p64
    rule _ITYPE:I32ValType . rem_u _I1 I2 => undefined            requires I2  ==MInt 0p32
    rule _ITYPE:I64ValType . rem_u _I1 I2 => undefined            requires I2  ==MInt 0p64

    rule ITYPE:I32ValType . div_s I1 I2 => < ITYPE > I1 /sMInt I2
      requires I2 =/=MInt 0p32
       andBool notBool (I1 ==MInt -2147483648p32 andBool I2 ==MInt -1p32)
    rule ITYPE:I64ValType . div_s I1 I2 => < ITYPE > I1 /sMInt I2
      requires I2 =/=MInt 0p64
       andBool notBool (I1 ==MInt -9223372036854775808p64 andBool I2 ==MInt -1p64)

    rule _ITYPE:I32ValType . div_s I1 I2 => undefined
      requires I2 ==MInt 0p32 orBool (I1 ==MInt -2147483648p32 andBool I2 ==MInt -1p32)
    rule _ITYPE:I64ValType . div_s I1 I2 => undefined
      requires I2 ==MInt 0p64 orBool (I1 ==MInt -9223372036854775808p64 andBool I2 ==MInt -1p64)

    rule ITYPE:I32ValType . rem_s I1 I2 => < ITYPE > I1 %sMInt I2
      requires I2 =/=MInt 0p32
       andBool notBool (I1 ==MInt -2147483648p32 andBool I2 ==MInt -1p32)
    rule ITYPE:I64ValType . rem_s I1 I2 => < ITYPE > I1 %sMInt I2
      requires I2 =/=MInt 0p64
       andBool notBool (I1 ==MInt -9223372036854775808p64 andBool I2 ==MInt -1p64)

    rule ITYPE:I32ValType . rem_s I1 I2 => < ITYPE > 0p32
      requires I1 ==MInt -2147483648p32 andBool I2 ==MInt -1p32
    rule ITYPE:I64ValType . rem_s I1 I2 => < ITYPE > 0p64
      requires I1 ==MInt -9223372036854775808p64 andBool I2 ==MInt -1p64

    rule _ITYPE:I32ValType . rem_s _I1 I2 => undefined
      requires I2 ==MInt 0p32
    rule _ITYPE:I64ValType . rem_s _I1 I2 => undefined
      requires I2 ==MInt 0p64
```

- `and` returns the bitwise conjunction of the 2 given floats.
- `or` returns the bitwise disjunction of the 2 given floats.
- `xor` returns the bitwise exclusive disjunction of the 2 given floats.

Of the bitwise operators, `and` will not overflow, but `or` and `xor` could.
These simply are the lifted K operators.

```k
    rule ITYPE:I32ValType . and I1 I2 => < ITYPE > I1 &MInt   I2
    rule ITYPE:I32ValType . or  I1 I2 => < ITYPE > I1 |MInt   I2
    rule ITYPE:I32ValType . xor I1 I2 => < ITYPE > I1 xorMInt I2
    rule ITYPE:I64ValType . and I1 I2 => < ITYPE > I1 &MInt   I2
    rule ITYPE:I64ValType . or  I1 I2 => < ITYPE > I1 |MInt   I2
    rule ITYPE:I64ValType . xor I1 I2 => < ITYPE > I1 xorMInt I2
```

- `shl` returns the result of shifting the first operand left by k bits modulo 2^N, in which k is the second operand modulo N.
- `shr_u` returns the result of shifting the first operand right by k bits, and extended with 0 bits.
- `shr_s` returns the result of shifting the first operand right by k bits, and  extended with the most significant bit of the original value

Similarly, K bitwise shift operators are lifted for `shl` and `shr_u`.
Careful attention is made for the signed version `shr_s`.

```k
    rule ITYPE:I32ValType . shl   I1 I2 => < ITYPE > I1 <<MInt I2
    rule ITYPE:I64ValType . shl   I1 I2 => < ITYPE > I1 <<MInt I2
    rule ITYPE:I32ValType . shr_u I1 I2 => < ITYPE > I1 >>lMInt I2
    rule ITYPE:I64ValType . shr_u I1 I2 => < ITYPE > I1 >>lMInt I2
    rule ITYPE:I32ValType . shr_s I1 I2 => < ITYPE > I1 >>aMInt I2
    rule ITYPE:I64ValType . shr_s I1 I2 => < ITYPE > I1 >>aMInt I2
```

- `rotl` returns the result of rotating the first operand left by k bits, in which k is the second operand modulo N.
- `rotr` returns the result of rotating the first operand right by k bits, in which k is the second operand modulo N.

The rotation operators `rotl` and `rotr` do not have appropriate K builtins, and so are built with a series of shifts.

```k
    rule ITYPE:I32ValType . rotl I1 I2 => < ITYPE > (I1 <<MInt (I2 &MInt 31p32)) |MInt (I1 >>lMInt ((--MInt I2) &MInt 31p32))
    rule ITYPE:I64ValType . rotl I1 I2 => < ITYPE > (I1 <<MInt (I2 &MInt 63p64)) |MInt (I1 >>lMInt ((--MInt I2) &MInt 63p64))
    rule ITYPE:I32ValType . rotr I1 I2 => < ITYPE > (I1 >>lMInt (I2 &MInt 31p32)) |MInt (I1 <<MInt ((--MInt I2) &MInt 31p32))
    rule ITYPE:I64ValType . rotr I1 I2 => < ITYPE > (I1 >>lMInt (I2 &MInt 63p64)) |MInt (I1 <<MInt ((--MInt I2) &MInt 63p64))
```

#### Binary Operators for Floats

There are 7 binary operators for integers: `add`, `sub`, `mul`, `div`, `min`, `max`, `copysign`.

- `add` returns the result of adding the 2 given floats and rounded to the nearest representable value.
- `sub` returns the result of substracting the second oprand from the first oprand and rounded to the nearest representable value.
- `mul` returns the result of multiplying the 2 given floats and rounded to the nearest representable value.
- `div` returns the result of dividing the first oprand by the second oprand and rounded to the nearest representable value.
- `min` returns the smaller value of the 2 given floats.
- `max` returns the bigger value of the 2 given floats.
- `copysign` returns the first oprand if the 2 given floats have the same sign, otherwise returns the first oprand with negated sign.

Note: For operators that defined under both sorts `IXXOp` and `FXXOp`, we need to give it a `klabel` and define it as a `symbol` to prevent parsing issue.

```k
    rule FTYPE:FValType . add      F1 F2 => < FTYPE > F1 +Float F2
    rule FTYPE:FValType . sub      F1 F2 => < FTYPE > F1 -Float F2
    rule FTYPE:FValType . mul      F1 F2 => < FTYPE > F1 *Float F2
    rule FTYPE          . div      F1 F2 => < FTYPE > F1 /Float F2
    rule FTYPE          . min      F1 F2 => < FTYPE > minFloat (F1, F2)
    rule FTYPE          . max      F1 F2 => < FTYPE > maxFloat (F1, F2)
    rule FTYPE          . copysign F1 F2 => < FTYPE > F1                requires signFloat (F1) ==Bool  signFloat (F2)
    rule FTYPE          . copysign F1 F2 => < FTYPE > --Float  F1       requires signFloat (F1) =/=Bool signFloat (F2)
```

### Test Operators

Test operations consume one operand and produce a bool, which is an `i32` value.
There is no test operation for float numbers.

```k
    syntax Val ::= I32ValType "." TestOp MInt{32} [symbol(intTestOp32), function, total]
                 | I64ValType "." TestOp MInt{64} [symbol(intTestOp64), function, total]
 // ----------------------------------------------------------------------------------
```

#### Test Operators for Integers

- `eqz` checks wether its operand is 0.

```k
    rule _ . eqz I => < i32 > #bool(I ==MInt 0p32)
    rule _ . eqz I => < i32 > #bool(I ==MInt 0p64)
```

### Relationship Operators

Relationship Operators consume two operands and produce a bool, which is an `i32` value.

```k
    syntax Val ::= I32ValType "." IRelOp MInt{32}   MInt{32}   [symbol(intRelOp32), function, total]
                 | I64ValType "." IRelOp MInt{64}   MInt{64}   [symbol(intRelOp64), function, total]
                 | FValType "." FRelOp Float Float [symbol(floatRelOp), function]
 // -----------------------------------------------------------------------------
```

Make intRelOp total.

```k

rule _:I32ValType . _:IRelOp _:MInt{32} _:MInt{32} => undefined  [owise]
rule _:I64ValType . _:IRelOp _:MInt{64} _:MInt{64} => undefined  [owise]

```

### Relationship Operators for Integers

There are 6 relationship operators for integers: `eq`, `ne`, `lt_sx`, `gt_sx`, `le_sx` and `ge_sx`.

- `eq` returns 1 if the 2 given integers are equal, 0 otherwise.
- `eq` returns 1 if the 2 given integers are not equal, 0 otherwise.

```k
    rule _:I32ValType . eq I1 I2 => < i32 > #bool(I1 ==MInt  I2)
    rule _:I64ValType . eq I1 I2 => < i32 > #bool(I1 ==MInt  I2)
    rule _:I32ValType . ne I1 I2 => < i32 > #bool(I1 =/=MInt I2)
    rule _:I64ValType . ne I1 I2 => < i32 > #bool(I1 =/=MInt I2)
```

- `lt_sx` returns 1 if the first oprand is less than the second opeand, 0 otherwise.
- `gt_sx` returns 1 if the first oprand is greater than the second opeand, 0 otherwise.

```k
    rule _:I32ValType     . lt_u I1 I2 => < i32 > #bool(I1 <uMInt I2)
    rule _:I64ValType     . lt_u I1 I2 => < i32 > #bool(I1 <uMInt I2)
    rule _:I32ValType     . gt_u I1 I2 => < i32 > #bool(I1 >uMInt I2)
    rule _:I64ValType     . gt_u I1 I2 => < i32 > #bool(I1 >uMInt I2)

    rule _:I32ValType     . lt_s I1 I2 => < i32 > #bool(I1 <sMInt I2)
    rule _:I64ValType     . lt_s I1 I2 => < i32 > #bool(I1 <sMInt I2)
    rule _:I32ValType     . gt_s I1 I2 => < i32 > #bool(I1 >sMInt I2)
    rule _:I64ValType     . gt_s I1 I2 => < i32 > #bool(I1 >sMInt I2)
```

- `le_sx` returns 1 if the first oprand is less than or equal to the second opeand, 0 otherwise.
- `ge_sx` returns 1 if the first oprand is greater than or equal to the second opeand, 0 otherwise.

```k
    rule _:I32ValType     . le_u I1 I2 => < i32 > #bool(I1 <=uMInt I2)
    rule _:I64ValType     . le_u I1 I2 => < i32 > #bool(I1 <=uMInt I2)
    rule _:I32ValType     . ge_u I1 I2 => < i32 > #bool(I1 >=uMInt I2)
    rule _:I64ValType     . ge_u I1 I2 => < i32 > #bool(I1 >=uMInt I2)

    rule _:I32ValType     . le_s I1 I2 => < i32 > #bool(I1 <=sMInt I2)
    rule _:I64ValType     . le_s I1 I2 => < i32 > #bool(I1 <=sMInt I2)
    rule _:I32ValType     . ge_s I1 I2 => < i32 > #bool(I1 >=sMInt I2)
    rule _:I64ValType     . ge_s I1 I2 => < i32 > #bool(I1 >=sMInt I2)
```

### Relationship Operators for Floats

There are 6 relationship operators for floats: `eq`, `ne`, `lt`, `gt`, `le` and `ge`.

- `eq` returns 1 if the 2 given floats are equal, 0 otherwise.
- `ne` returns 1 if the 2 given floats are not equal, 0 otherwise.
- `lt` returns 1 if the first oprand is less than the second opeand, 0 otherwise.
- `gt` returns 1 if the first oprand is greater than the second opeand, 0 otherwise.
- `le` returns 1 if the first oprand is less than or equal to the second opeand, 0 otherwise.
- `ge` returns 1 if the first oprand is greater than or equal to the second opeand, 0 otherwise.

```k
    rule _          . lt F1 F2 => < i32 > #bool(F1 <Float   F2)
    rule _          . gt F1 F2 => < i32 > #bool(F1 >Float   F2)
    rule _          . le F1 F2 => < i32 > #bool(F1 <=Float  F2)
    rule _          . ge F1 F2 => < i32 > #bool(F1 >=Float  F2)
    rule _:FValType . eq F1 F2 => < i32 > #bool(F1 ==Float  F2)
    rule _:FValType . ne F1 F2 => < i32 > #bool(F1 =/=Float F2)
```

### Conversion Operators

Conversion operators always take a single argument as input and cast it to another type.
The operators are further broken down into subsorts for their input type, for simpler type-checking.

```k
    syntax Val ::= ValType "." CvtOp Number [symbol(numberCvtOp), function, total]
 // -----------------------------------------------------------------------
    rule _:ValType . _:CvtOp _:Number => undefined      [owise]
```

There are 7 conversion operators: `wrap`, `extend`, `trunc`, `convert`, `demote` ,`promote` and `reinterpret`.

- `wrap` takes an `i64` value, cuts of the 32 most significant bits and returns an `i32` value.

```k
    rule i32 . wrap_i64 I:MInt{64} => < i32 > roundMInt(I)
```

- `extend` takes an `i32` type value, converts its type into the `i64` and returns the result.

```k
    rule i64 . extend_i32_u I:MInt{32} => < i64 > roundMInt(I)
    rule i64 . extend_i32_s I:MInt{32} => < i64 > signExtendMInt(I)
```

- `convert` takes an `int` type value and convert it to the nearest `float` type value.

```k
    rule FTYPE . convert_i32_s I:MInt{32} => #round( FTYPE , MInt2Signed(I) )
    rule FTYPE . convert_i32_u I:MInt{32} => #round( FTYPE , MInt2Unsigned(I) )

    rule FTYPE . convert_i64_s I:MInt{64} => #round( FTYPE , MInt2Signed(I) )
    rule FTYPE . convert_i64_u I:MInt{64} => #round( FTYPE , MInt2Unsigned(I) )
```

- `demote` turns an `f64` type value to the nearest `f32` type value.
- `promote` turns an `f32` type value to the nearest `f64` type value:

```k
    rule f64 . promote_f32 F => #round( f64 , F )

    rule f32 . demote_f64  F => #round( f32 , F )
```

- `trunc` first truncates a float value, then convert the result to the nearest integer value.

```k
    rule ITYPE . trunc_f32_s F => undefined
      requires #isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE))
    rule ITYPE . trunc_f32_u F => undefined
      requires #isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0)

    rule ITYPE:I32ValType . trunc_f32_s F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE)))
    rule ITYPE:I64ValType . trunc_f32_s F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE)))
    rule ITYPE:I32ValType . trunc_f32_u F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0))
    rule ITYPE:I64ValType . trunc_f32_u F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0))

    rule ITYPE . trunc_f64_s F => undefined
      requires #isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE))
    rule ITYPE . trunc_f64_u F => undefined
      requires #isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0)

    rule ITYPE:I32ValType . trunc_f64_s F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE)))
    rule ITYPE:I64ValType . trunc_f64_s F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow1(ITYPE)) orBool (0 -Int Float2Int(truncFloat(F)) >Int #pow1 (ITYPE)))
    rule ITYPE:I32ValType . trunc_f64_u F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0))
    rule ITYPE:I64ValType . trunc_f64_u F => <ITYPE> Int2MInt(Float2Int(truncFloat(F)))
      requires notBool (#isInfinityOrNaN (F) orBool (Float2Int(truncFloat(F)) >=Int #pow (ITYPE)) orBool (Float2Int(truncFloat(F)) <Int 0))
```

**TODO**: Unimplemented: `inn.reinterpret_fnn`,  `fnn.reinterpret_inn`.

```k
endmodule
```
