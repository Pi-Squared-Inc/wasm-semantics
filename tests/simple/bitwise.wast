(i32.const 20)
(i32.const 18)
(i32.and)
#assertTopStack < i32 > i2i32(16) "and"

(i32.const 20)
(i32.const 18)
(i32.or)
#assertTopStack < i32 > i2i32(22) "or"

(i32.const 20)
(i32.const 18)
(i32.xor)
#assertTopStack < i32 > i2i32(6) "xor"

(i32.const 2)
(i32.const 1)
(i32.shl)
#assertTopStack < i32 > i2i32(4) "shl 1"

(i32.const 2)
(i32.add (i32.const 2147483648) (i32.const 1))
(i32.shl)
#assertTopStack < i32 > i2i32(4) "shl 2"

(i32.const 2147483648)
(i32.const 2)
(i32.shr_u)
#assertTopStack < i32 > i2i32(536870912) "shr_u 1" ;; 2 ^Int 29

(i32.const 2)
(i32.const 2)
(i32.shr_u)
#assertTopStack < i32 > i2i32(0) "shr_u 2"

(i32.sub (i32.const 4294967296) (i32.const 2))
(i32.const 1)
(i32.shr_s)
#assertTopStack < i32 > i2i32(4294967295) "shr_s 1" ;; #pow(i32) -Int 1

(i32.const 2)
(i32.const 2)
(i32.shr_s)
#assertTopStack < i32 > i2i32(0) "shr_s 2"

(i32.add (i32.const 2147483648) (i32.const 2))
(i32.const 3)
(i32.rotl)
#assertTopStack < i32 > i2i32(20) "rotl"

(i32.add (i32.const 2147483648) (i32.const 16))
(i32.const 3)
(i32.rotr)
#assertTopStack < i32 > i2i32(268435458) "rotr" ;; 2 ^Int 28 +Int 2

;; clz

(i32.const 2147483648)
(i32.clz)
#assertTopStack < i32 > i2i32(0) "clz #pow1(i32)"
(i64.const 9223372036854775808)
(i64.clz)
#assertTopStack < i64 > i2i64(0) "clz #pow1(i62)"

(i32.const 0)
(i32.clz)
#assertTopStack < i32 > i2i32(32) "clz 0"
(i64.const 0)
(i64.clz)
#assertTopStack < i64 > i2i64(64) "clz 0"

(i32.const 1)
(i32.clz)
#assertTopStack < i32 > i2i32(31) "clz 1"
(i64.const 1)
(i64.clz)
#assertTopStack < i64 > i2i64(63) "clz 1"

(i32.sub (i32.const 4294967296) (i32.const 1))
(i32.clz)
#assertTopStack < i32 > i2i32(0) "clz 2^32 - 1"

(i64.sub (i64.const 18446744073709551616) (i64.const 1))
(i64.clz)
#assertTopStack < i64 > i2i64(0) "clz 2^64 - 1"

(i32.sub (i32.const 2147483648) (i32.const 1))
(i32.clz)
#assertTopStack < i32 > i2i32(1) "clz 2^31 - 1"

(i64.sub (i64.const 9223372036854775808) (i64.const 1))
(i64.clz)
#assertTopStack < i64 > i2i64(1) "clz 2^63 - 1"

;; ctz
(i32.const 2147483648)
(i32.ctz)
#assertTopStack < i32 > i2i32(31) "ctz #pow1(i32)"
(i64.const 9223372036854775808)
(i64.ctz)
#assertTopStack < i64 > i2i64(63) "ctz #pow1(i32)"

(i32.const 0)
(i32.ctz)
#assertTopStack < i32 > i2i32(32) "ctz 0"
(i64.const 0)
(i64.ctz)
#assertTopStack < i64 > i2i64(64) "ctz 0"

(i32.const 1)
(i32.ctz)
#assertTopStack < i32 > i2i32(0) "ctz 1"
(i64.const 1)
(i64.ctz)
#assertTopStack < i64 > i2i64(0) "ctz 1"

(i32.sub (i32.const 4294967296) (i32.const 1))
(i32.ctz)
#assertTopStack < i32 > i2i32(0) "ctz 2^32 - 1"
(i64.sub (i64.const 18446744073709551616) (i64.const 1))
(i64.ctz)
#assertTopStack < i64 > i2i64(0) "ctz 2^64 - 1"

;; popcnt

(i32.const 2147483648)
(i32.popcnt)
#assertTopStack < i32 > i2i32(1) "popcnt #pow1(i32)"
(i64.const 9223372036854775808)
(i64.popcnt)
#assertTopStack < i64 > i2i64(1) "popcnt #pow1(i32)"

(i32.const 0)
(i32.popcnt)
#assertTopStack < i32 > i2i32(0) "popcnt 0"
(i64.const 0)
(i64.popcnt)
#assertTopStack < i64 > i2i64(0) "popcnt 0"

(i32.const 1)
(i32.popcnt)
#assertTopStack < i32 > i2i32(1) "popcnt 1"
(i64.const 1)
(i64.popcnt)
#assertTopStack < i64 > i2i64(1) "popcnt 1"

(i32.sub (i32.const 4294967296) (i32.const 1))
(i32.popcnt)
#assertTopStack < i32 > i2i32(32) "popcnt 2^32 - 1"
(i64.sub (i64.const 18446744073709551616) (i64.const 1))
(i64.popcnt)
#assertTopStack < i64 > i2i64(64) "popcnt 2^64 - 1"

#clearConfig
