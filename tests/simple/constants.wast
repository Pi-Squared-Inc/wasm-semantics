;; Integers
;; --------

(i32.const 3)
#assertTopStack < i32 > i2i32(3) "i32 1"

(i32.const 5)
#assertTopStack < i32 > i2i32(5) "i32 parens"

(i64.const 71)
#assertTopStack < i64 > i2i64(71) "i64"

(i32.const -5)
#assertTopStack < i32 > i2i32(4294967291) "i32 manual unsigned" ;; #pow(i32) -Int 5

(i32.sub (i32.const 4294967296) (i32.const 5))
#assertTopStack < i32 > i2i32(-5) "i32 manual unsigned"

(i32.const -5)
#assertTopStack < i32 > i2i32(-5) "i32 signed constant"

(i32.const 4294967291)
#assertTopStack < i32 > i2i32(-5) "i32 signed assert"

(i32.add (i32.const 4294967296) (i32.const 1))
#assertTopStack < i32 > i2i32(1) "i32 overflow"

(i32.const -1)
#assertTopStackExactly < i32 > i2i32(4294967295) "i32 overflow"

(i64.const -1)
#assertTopStackExactly < i64 > i2i64(18446744073709551615) "i62 overflow" ;; #pow(i64) -Int 1

;; Floating point
;; --------------

(f32.const 3.245)
#assertTopStack < f32 > 3.245 "f32"

(f64.const 3.234523)
#assertTopStack < f64 > 3.234523 "f32 parens"

(f64.const 1.21460644e+52)
#assertTopStack < f64 > 1.21460644e+52 "f64 scientific 1"

(f64.const 1.6085927714e-321)
#assertTopStack < f64 > 1.6085927714e-321 "f64 scientific 2"

(f64.const 1.63176601e-302)
#assertTopStack < f64 > 1.63176601e-302 "f64 scientific 3"

;; Below examples do not work with current float parser
;; (f64.const 0x1.da21c460a6f44p+52)
;; (f64.const 0x1.60859d2e7714ap-321)
;; (f64.const 0x1.e63f1b7b660e1p-302)

;; Helper conversions
;; ------------------

(i32.const 0)
#assertTopStack < i32 > i2i32(0) "#unsigned . #signed 1"

(i32.const 2147483648)
#assertTopStack < i32 > i2i32(-2147483648) "#unsigned . #signed 2"

(i64.const 0)
#assertTopStack < i64 > i2i64(0) "#unsigned . #signed 4"

(i64.const 9223372036854775808)
#assertTopStack < i64 > i2i64(-9223372036854775808) "#unsigned . #signed 5"

#clearConfig
