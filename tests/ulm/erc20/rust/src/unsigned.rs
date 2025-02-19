// This is a suboptimal implementation of an unsigned int, which is small and
// therefore useful for testing the wasm semantics. A proper implementation
// should probably use something like ruint2::Uint<..., ...> or uint256::Uint256.

use bytes::{Bytes, Buf};
use core::cmp::Ordering;
use core::ops::Add;
use core::ops::Sub;

use crate::assertions::fail;
use crate::require;
use crate::encoder::{Encodable, EncodingType, EncodingType::FixedSize};
use crate::decoder::Decodable;
use crate::predicate::{Satisfied};

#[derive(Debug)]
pub struct Unsigned<const N: usize> {
    chunks: [u8; N],
}

// pub type U72  = Unsigned<9>;
// pub type U80  = Unsigned<10>;
// pub type U88  = Unsigned<11>;
// pub type U96  = Unsigned<12>;
// pub type U104 = Unsigned<13>;
// pub type U112 = Unsigned<14>;
// pub type U120 = Unsigned<15>;
// pub type U128 = Unsigned<16>;
// pub type U136 = Unsigned<17>;
// pub type U144 = Unsigned<18>;
// pub type U152 = Unsigned<19>;
pub type U160 = Unsigned<20>;
// pub type U168 = Unsigned<21>;
// pub type U176 = Unsigned<22>;
// pub type U184 = Unsigned<23>;
// pub type U192 = Unsigned<24>;
// pub type U200 = Unsigned<25>;
// pub type U208 = Unsigned<26>;
// pub type U216 = Unsigned<27>;
// pub type U224 = Unsigned<28>;
// pub type U232 = Unsigned<29>;
// pub type U240 = Unsigned<30>;
// pub type U248 = Unsigned<31>;
pub type U256 = Unsigned<32>;

impl<const N: usize> Unsigned<N> {
    pub fn try_from_unsigned<const M: usize>(value: &Unsigned<M>) -> Result<Unsigned<N>, &'static str> {
        let mut chunks = [0_u8; N];
        if M <= N {
            for i in 0 .. M {
                chunks[i] = value.chunks[i];
            }
        } else {
            for i in 0 .. N {
                chunks[i] = value.chunks[i];
            }
            for i in N .. M {
                if value.chunks[i] != 0 {
                    return Err("Value too large to cast");
                }
            }
        }
        Ok (Unsigned { chunks })
    }

    pub fn from_array_le(chunks: [u8; N]) -> Unsigned<N> {
        Unsigned { chunks }
    }

    pub fn from_array_be(chunks: [u8; N]) -> Unsigned<N> {
        let r_c_v : Vec<u8> = chunks.into_iter().rev().collect();
        let reverse_chunks: [u8; N] = r_c_v.try_into().unwrap();
        Unsigned { chunks: reverse_chunks }
    }

    pub fn from_u64(value: u64) -> Unsigned<N> {
        if 8 <= N {
            let mut chunks = [0_u8; N];
            let mut to_process = value;
            for i in 0 .. 8 {
                chunks[i] = (to_process & 0xff) as u8;
                to_process = to_process >> 8;
            }
            require!(to_process == 0, "Unprocessed bits in value.");
            Unsigned { chunks }
        } else {
            match Unsigned::try_from_unsigned(&Unsigned::<8>::from_u64(value)) {
                Ok(v) => v,
                Err(msg) => fail(msg),
            }
        }
    }
    pub fn from_bool(value:bool) -> Self {
        Self::from_u64(if value {0} else {1})
    }
    pub fn from_u8(value:u8) -> Self {
        Self::from_u64(value as u64)
    }
    pub fn from_u16(value:u16) -> Self {
        Self::from_u64(value as u64)
    }
    pub fn from_u32(value:u32) -> Self {
        Self::from_u64(value as u64)
    }

    pub fn copy_to_array_le(&self, chunks: &mut [u8; N]) {
        chunks.copy_from_slice(&self.chunks);
    }

    pub fn try_to_u64(&self) -> Result<u64, &'static str> {
        let useful_length =
            if 8 < N {
                for i in 8 .. N {
                    if self.chunks[i] != 0 {
                        return Err("Overflow when converting to u64");
                    }
                }
                8
            } else {
                N
            };
        let mut value = 0_u64;
        for i in (0 .. useful_length).rev() {
            value = value << 8;
            value += self.chunks[i] as u64;
        }
        Ok(value)
    }
}

impl<const N: usize> TryFrom<&Unsigned<N>> for u64 {
    type Error = &'static str;
    fn try_from(value: &Unsigned<N>) -> Result<Self, Self::Error> {
        value.try_to_u64()
    }
}
impl<const N: usize> TryFrom<Unsigned<N>> for u64 {
    type Error = &'static str;
    fn try_from(value: Unsigned<N>) -> Result<Self, Self::Error> {
        (&value).try_into()
    }
}
impl<const N: usize> TryFrom<&Unsigned<N>> for usize {
    type Error = &'static str;
    fn try_from(value: &Unsigned<N>) -> Result<Self, Self::Error> {
        let value_u64: u64 = value.try_into()?;
        match value_u64.try_into() {
            Ok(v) => Ok(v),
            Err(_) => Err("Error converting u64 to usize")
        }
    }
}
impl<const N: usize> TryFrom<Unsigned<N>> for usize {
    type Error = &'static str;
    fn try_from(value: Unsigned<N>) -> Result<Self, Self::Error> {
        (&value).try_into()
    }
}
impl<const N: usize, const M: usize> TryFrom<&Unsigned<N>> for Unsigned<M> {
    type Error = &'static str;
    fn try_from(value: &Unsigned<N>) -> Result<Self, Self::Error> {
        Unsigned::try_from_unsigned(value)
    }
}

#[macro_export]
macro_rules! try_from_u256 {
    ( $size:expr ) => {
        impl TryFrom<U256> for Unsigned<$size>
        {
            type Error = &'static str;
            fn try_from(value: U256) -> Result<Self, Self::Error> {
                (&value).try_into()
            }
        }
        impl From<Unsigned<$size>> for U256
            where SmallerThan32<$size>: Satisfied
        {
            fn from(value: Unsigned<$size>) -> Self {
                (&value).try_into().unwrap()
            }
        }
    }
}
try_from_u256!(1);
try_from_u256!(2);
try_from_u256!(3);
try_from_u256!(4);
try_from_u256!(5);
try_from_u256!(6);
try_from_u256!(7);
try_from_u256!(8);
try_from_u256!(9);
try_from_u256!(10);
try_from_u256!(11);
try_from_u256!(12);
try_from_u256!(13);
try_from_u256!(14);
try_from_u256!(15);
try_from_u256!(16);
try_from_u256!(17);
try_from_u256!(18);
try_from_u256!(19);
try_from_u256!(20);
try_from_u256!(21);
try_from_u256!(22);
try_from_u256!(23);
try_from_u256!(24);
try_from_u256!(25);
try_from_u256!(26);
try_from_u256!(27);
try_from_u256!(28);
try_from_u256!(29);
try_from_u256!(30);
try_from_u256!(31);

impl<const N: usize> Add for &Unsigned<N> {
    type Output = Unsigned<N>;
    fn add(self, other: &Unsigned<N>) -> Self::Output {
        let mut chunks = [0_u8; N];
        let mut carry = 0_u16;
        for i in 0..N {
            let value = (self.chunks[i] as u16) + (other.chunks[i] as u16) + carry;
            carry = value >> 8;
            chunks[i] = (value & 0xff) as u8;
        }
        require!(carry == 0, "Addition overflow");
        Unsigned { chunks }
    }
}
impl<const N: usize> Add for Unsigned<N> {
    type Output = Unsigned<N>;
    fn add(self, other: Unsigned<N>) -> Self::Output {
        &self + &other
    }
}
impl<const N: usize> Add<Unsigned<N>> for &Unsigned<N> {
    type Output = Unsigned<N>;
    fn add(self, other: Unsigned<N>) -> Self::Output {
        self + &other
    }
}
impl<const N: usize> Add<&Unsigned<N>> for Unsigned<N> {
    type Output = Unsigned<N>;
    fn add(self, other: &Unsigned<N>) -> Self::Output {
        &self + other
    }
}

impl<const N: usize> Sub for &Unsigned<N> {
    type Output = Unsigned<N>;
    fn sub(self, other: &Unsigned<N>) -> Self::Output {
        let mut chunks = [0_u8; N];
        let mut carry = 0_u16;
        for i in 0..N {
            let self_chunk = self.chunks[i] as u16;
            let to_remove = other.chunks[i] as u16 + carry;
            let remove_from =
                if self_chunk >= to_remove {
                    carry = 0;
                    self_chunk
                } else {
                    carry = 1;
                    self_chunk + 0x100
                };
            require!(remove_from >= to_remove, "Unexpected value in subtraction");
            let result = remove_from - to_remove;
            require!(result <= 0xff, "Unexpected value in subtraction");
            chunks[i] = result as u8;
        }
        require!(carry == 0, "Subtraction overflow");
        Unsigned { chunks }
    }
}
impl<const N: usize> Sub for Unsigned<N> {
    type Output = Unsigned<N>;
    fn sub(self, other: Unsigned<N>) -> Self::Output {
        &self - &other
    }
}
impl<const N: usize> Sub<Unsigned<N>> for &Unsigned<N> {
    type Output = Unsigned<N>;
    fn sub(self, other: Unsigned<N>) -> Self::Output {
        self - &other
    }
}
impl<const N: usize> Sub<&Unsigned<N>> for Unsigned<N> {
    type Output = Unsigned<N>;
    fn sub(self, other: &Unsigned<N>) -> Self::Output {
        &self - other
    }
}

impl<const N: usize> Ord for Unsigned<N> {
    fn cmp(&self, other: &Self) -> Ordering {
        for i in (0..N).rev() {
            if self.chunks[i] < other.chunks[i] {
                return Ordering::Less;
            }
            if self.chunks[i] > other.chunks[i] {
                return Ordering::Greater;
            }
        }
        Ordering::Equal
    }
}
impl<const N: usize> PartialOrd for Unsigned<N> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
impl<const N: usize> PartialEq for Unsigned<N> {
    fn eq(&self, other: &Self) -> bool {
        self.cmp(other) == Ordering::Equal
    }
}
impl<const N: usize> Eq for Unsigned<N> {}
impl<const N: usize> Clone for Unsigned<N> {
    fn clone(&self) -> Self {
        Unsigned { chunks: self.chunks.clone() }
    }
}

impl Encodable for U256
{
    fn encode(&self) -> (EncodingType, Bytes) {
        let mut encoded = [0_u8; 32];
        for i in 0 .. 32 {
            encoded[i] = self.chunks[31 - i];
        }
        (FixedSize, Bytes::copy_from_slice(&encoded))
    }
}
impl Decodable for U256
{
    fn encoding_type() -> EncodingType {
        FixedSize
    }
    fn head_size() -> usize {
        32
    }
    fn decode(bytes: Bytes) -> Self {
        let encoded = bytes.chunk();
        require!(32 == encoded.len(), "Wrong length to decode");
        let mut value: U256 = U256::from_u64(0);
        for i in 0 .. 32 {
            value.chunks[31 - i] = encoded[i];
        }
        value
    }
}
impl<const N: usize> Encodable for Unsigned<N>
where
    SmallerThan32<N>: Satisfied
{
    fn encode(&self) -> (EncodingType, Bytes) {
        match U256::try_from_unsigned(self) {
            Ok(v) => v.encode(),
            Err(msg) => fail(msg),
        }
    }
}
impl<const N: usize> Decodable for Unsigned<N>
where
    SmallerThan32<N>: Satisfied
{
    fn encoding_type() -> EncodingType {
        U256::encoding_type()
    }
    fn head_size() -> usize {
        U256::head_size()
    }
    fn decode(bytes: Bytes) -> Self {
        let value_u256 = U256::decode(bytes);
        match Unsigned::<N>::try_from_unsigned(&value_u256) {
            Ok(v) => v,
            Err(msg) => fail(msg),
        }
    }
}

pub enum SmallerThan32<const EXPRESSION: usize> {}
impl Satisfied for SmallerThan32<1> {}
impl Satisfied for SmallerThan32<2> {}
impl Satisfied for SmallerThan32<3> {}
impl Satisfied for SmallerThan32<4> {}
impl Satisfied for SmallerThan32<5> {}
impl Satisfied for SmallerThan32<6> {}
impl Satisfied for SmallerThan32<7> {}
impl Satisfied for SmallerThan32<8> {}
impl Satisfied for SmallerThan32<9> {}
impl Satisfied for SmallerThan32<10> {}
impl Satisfied for SmallerThan32<11> {}
impl Satisfied for SmallerThan32<12> {}
impl Satisfied for SmallerThan32<13> {}
impl Satisfied for SmallerThan32<14> {}
impl Satisfied for SmallerThan32<15> {}
impl Satisfied for SmallerThan32<16> {}
impl Satisfied for SmallerThan32<17> {}
impl Satisfied for SmallerThan32<18> {}
impl Satisfied for SmallerThan32<19> {}
impl Satisfied for SmallerThan32<20> {}
impl Satisfied for SmallerThan32<21> {}
impl Satisfied for SmallerThan32<22> {}
impl Satisfied for SmallerThan32<23> {}
impl Satisfied for SmallerThan32<24> {}
impl Satisfied for SmallerThan32<25> {}
impl Satisfied for SmallerThan32<26> {}
impl Satisfied for SmallerThan32<27> {}
impl Satisfied for SmallerThan32<28> {}
impl Satisfied for SmallerThan32<29> {}
impl Satisfied for SmallerThan32<30> {}
impl Satisfied for SmallerThan32<31> {}
