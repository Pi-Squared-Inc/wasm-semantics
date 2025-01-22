import os
from dataclasses import dataclass


def bytes_to_k(b: bytes) -> str:
    escaped_bytes = ''.join([f'\\x{b:02x}' for b in b])
    return 'b"' + escaped_bytes + '"'


class Constructor:
    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        raise NotImplementedError('Constructor.build')

    def needs_bwi(self) -> bool:
        raise NotImplementedError('Constructor.needs_bwi')


@dataclass(frozen=True)
class Symbol(Constructor):
    name: str

    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        output_pieces.append(f'instrResult(`{self.name}`(')
        first = True
        for i, arg in enumerate(args):
            if not arg.is_used_in_constructor():
                continue
            if not first:
                output_pieces.append(', ')
            first = False
            output_pieces.append(arg.rhs_argument(i, True))
        if first:
            output_pieces.append('.KList')
        output_pieces.append(f'), {bwi})')

    def needs_bwi(self) -> bool:
        return True


def symbol(s: str) -> Symbol:
    return Symbol(s)


class Identity(Constructor):
    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        first = True
        output_pieces.append('instrResult(')
        for i, arg in enumerate(args):
            if not arg.is_used_in_constructor():
                continue
            if not first:
                raise ValueError(f'Identity constructor requires exactly one argument: {args}')
            first = False
            output_pieces.append(arg.rhs_argument(i, True))
        output_pieces.append(f', {bwi})')

    def needs_bwi(self) -> bool:
        return True


def identity() -> Identity:
    return Identity()


class NotImplemented(Constructor):
    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        output_pieces.append('parseError("instruction not implemented",')
        for i, arg in enumerate(args):
            if not arg.is_used_in_constructor():
                continue
            if not arg.is_parsing_arg():
                continue
            output_pieces.append(f' ListItem({arg.rhs_argument(i, False)})')
        output_pieces.append(f' ListItem({bwi}))')

    def needs_bwi(self) -> bool:
        return True


def not_implemented() -> NotImplemented:
    return NotImplemented()


@dataclass(frozen=True)
class Parser(Constructor):
    parser_name: str

    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        output_pieces.append(f'{self.parser_name}(')
        first = True
        for i, arg in enumerate(args):
            if not arg.is_used_in_constructor():
                continue
            if not first:
                output_pieces.append(', ')
            first = False
            output_pieces.append(arg.rhs_argument(i, True))
        if not first:
            output_pieces.append(', ')
        output_pieces.append(f'{bwi})')

    def needs_bwi(self) -> bool:
        return True


def parser(s: str) -> Parser:
    return Parser(s)


@dataclass(frozen=True)
class ConstructorResult(Constructor):
    name: str

    def build(self, args: list['Argument'], bwi: str, output_pieces: list[str]) -> None:
        output_pieces.append(f'instrResult({self.name}')
        if args:
            first = True
            for i, arg in enumerate(args):
                if not arg.is_used_in_constructor():
                    continue
                if first:
                    output_pieces.append('(')
                    first = False
                else:
                    output_pieces.append(', ')
                output_pieces.append(arg.rhs_argument(i, True))
            if not first:
                output_pieces.append(')')
        output_pieces.append(f', {bwi})')

    def needs_bwi(self) -> bool:
        return True


class Argument:
    def parser(self, bwi: str) -> str:
        raise NotImplementedError('Argument.parser')

    def is_used_in_constructor(self) -> bool:
        raise NotImplementedError('Argument.is_used_in_constructor')

    def is_parsing_arg(self) -> bool:
        raise NotImplementedError('Argument.is_parsing_arg')

    def result_argument(self, index: int, bwi: str) -> str:
        raise NotImplementedError('Argument.result_argument')

    def result_type(self) -> str:
        raise NotImplementedError('Argument.result_type')

    def value_type(self) -> str:
        raise NotImplementedError('Argument.value_type')

    def lhs_argument(self, index: int, unused: bool) -> str:
        raise NotImplementedError('Argument.lhs_argument')

    def rhs_argument(self, index: int, cast_final_argument: bool) -> str:
        raise NotImplementedError('Argument.rhs_argument')


@dataclass(frozen=True)
class TypedArg(Argument):
    arg_type: str

    def parser(self, bwi: str) -> str:
        if self.arg_type == 'UnsignedInt':
            parse_fn = 'parseLeb128UInt'
        elif self.arg_type == 'SignedInt':
            parse_fn = 'parseLeb128SInt'
        else:
            parse_fn = f'parse{self.arg_type}'

        return f'{parse_fn}({bwi})'

    def is_used_in_constructor(self) -> bool:
        return True

    def is_parsing_arg(self) -> bool:
        return True

    def result_argument(self, index: int, bwi: str) -> str:
        t = self.result_type()
        it = self.inner_type()
        mid = ''
        if self.arg_type == 'Block':
            mid = ' _:Bool,'
        return f'{t[0].lower()}{t[1:]}({self.arg_type}{index}:{it},{mid} {bwi}:BytesWithIndex)'

    def result_type(self) -> str:
        t = self.inner_type()
        return f'{t}Result'

    def inner_type(self) -> str:
        if self.arg_type == 'UnsignedInt':
            return 'Int'
        if self.arg_type == 'SignedInt':
            return 'Int'
        if self.arg_type == 'UnsignedIntVec':
            return 'Ints'
        if self.arg_type == 'Float32':
            return 'Float'
        if self.arg_type == 'Float64':
            return 'Float'
        return self.arg_type

    def value_type(self) -> str:
        return self.inner_type()

    def lhs_argument(self, index: int, unused: bool) -> str:
        if unused:
            prefix = '_'
        else:
            prefix = ''
        return f'{prefix}{self.arg_type}{index}:{self.value_type()}'

    def rhs_argument(self, index: int, cast_final_argument: bool) -> str:
        if self.arg_type == 'MemArg' and cast_final_argument:
            return f'getMemArgOffset({self.arg_type}{index})'
        return f'{self.arg_type}{index}'


@dataclass(frozen=True)
class ConstructorArg(Argument):
    name: str

    def is_used_in_constructor(self) -> bool:
        return True

    def is_parsing_arg(self) -> bool:
        return False

    def rhs_argument(self, index: int, cast_final_argument: bool) -> str:
        return self.name


def constructor_arg(name: str) -> ConstructorArg:
    return ConstructorArg(name)


@dataclass(frozen=True)
class ParseOnlyConstant(Argument):
    value: bytes

    def parser(self, bwi: str) -> str:
        return f'parseConstant({bwi}, {bytes_to_k(self.value)})'

    def is_used_in_constructor(self) -> bool:
        return False

    def is_parsing_arg(self) -> bool:
        return True

    def result_argument(self, index: int, bwi: str) -> str:
        return f'{bwi}:BytesWithIndex'

    def result_type(self) -> str:
        return 'BytesWithIndexOrError'


def parse_constant(b: bytes) -> ParseOnlyConstant:
    return ParseOnlyConstant(b)


@dataclass(frozen=True)
class RepeatedBytes(Argument):
    count: int

    def parser(self, bwi: str) -> str:
        return f'ignoreBytes({bwi}, {self.count})'

    def is_used_in_constructor(self) -> bool:
        return False

    def is_parsing_arg(self) -> bool:
        return True

    def result_argument(self, index: int, bwi: str) -> str:
        return f'{bwi}:BytesWithIndex'

    def result_type(self) -> str:
        return 'BytesWithIndexOrError'


def repeated_bytes(count: int) -> RepeatedBytes:
    return RepeatedBytes(count)


@dataclass(frozen=True)
class RepeatedType(Argument):
    type_: str
    count: int

    def parser(self, bwi: str) -> str:
        return f'ignore{self.type_}({bwi}, {self.count})'

    def is_used_in_constructor(self) -> bool:
        return False

    def is_parsing_arg(self) -> bool:
        return True

    def result_argument(self, index: int, bwi: str) -> str:
        return f'{bwi}:BytesWithIndex'

    def result_type(self) -> str:
        return 'BytesWithIndexOrError'


def repeated_type(value_type: str, count: int) -> RepeatedType:
    return RepeatedType(value_type, count)


@dataclass(frozen=True)
class InstrConfig:
    name: str
    prefix: bytes
    args: list[Argument]
    constructor: Constructor

    def __init__(self, name: str, prefix: bytes, args: list[str | Argument], constructor: str | Constructor) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'prefix', prefix)
        object.__setattr__(self, 'args', [arg if isinstance(arg, Argument) else TypedArg(arg) for arg in args])
        object.__setattr__(
            self, 'constructor', constructor if isinstance(constructor, Constructor) else ConstructorResult(constructor)
        )

    def with_prefix(self, p: bytes) -> 'InstrConfig':
        return InstrConfig(self.name, p, list(self.args), self.constructor)


# fmt: off
INSTRS_CONFIG:list[InstrConfig]=[
    # Wasm _control instructions_ are encoded with the follow tags.
    # Note that `ELSE` instructions must appear in conjunction with `IF` instructions.

    # The tuple structure is:
    # ('INSTRUCTION_NAME', b'instruction-prefix', ['Argument1Type', 'Argument2Type', ...], '#ConstructorName')
    InstrConfig('UNREACHABLE', b'\x00', [], 'unreachable'),
    InstrConfig('NOP', b'\x01', [], 'nop'),
    InstrConfig('BLOCK', b'\x02', ['Block', ], identity()),  # #block
    InstrConfig('LOOP', b'\x03', ['Block', ], 'loop'),  # #loop
    InstrConfig('IF', b'\x04', [], parser('parseIf')),
    # ('ELSE', b'\x05', [], ''),  -- Parsed as part of 'If'
    InstrConfig('BR', b'\x0C', ['UnsignedInt', ], '#br'),
    InstrConfig('BR_IF', b'\x0D', ['UnsignedInt', ], '#br_if'),
    InstrConfig('BR_TABLE', b'\x0E', ['UnsignedIntVec', 'UnsignedInt', ], 'buildBrTable'),
    InstrConfig('RETURN', b'\x0F', [], 'return'),
    InstrConfig('CALL', b'\x10', ['UnsignedInt', ], '#call'),
    InstrConfig('CALL_INDIRECT', b'\x11', ['UnsignedInt', 'UnsignedInt', ], 'buildCallIndirect'),  # #call_indirect

    # _Reference instructions_ are encoded with the following tags:

    InstrConfig('REF_NULL', b'\xD0', ['HeapType', ], symbol('aRef.null')),
    InstrConfig('REF_ISNULL', b'\xD1', [], '#ref.is_null'),
    InstrConfig('REF_FUNC', b'\xD2', ['UnsignedInt', ], '#ref.func'),

    InstrConfig('DROP', b'\x1A', [], 'drop'),
    InstrConfig('SELECT', b'\x1B', [], 'select'),
    InstrConfig('SELECT_GENERIC', b'\x1C', ['ValTypes', ], not_implemented()),

    # _Variable instructions_ are encoded with the following tags:

    InstrConfig('LOCAL_GET', b'\x20', ['UnsignedInt', ], '#local.get'),
    InstrConfig('LOCAL_SET', b'\x21', ['UnsignedInt', ], '#local.set'),
    InstrConfig('LOCAL_TEE', b'\x22', ['UnsignedInt', ], '#local.tee'),
    InstrConfig('GLOBAL_GET', b'\x23', ['UnsignedInt', ], '#global.get'),
    InstrConfig('GLOBAL_SET', b'\x24', ['UnsignedInt', ], '#global.set'),

    # _Table instructions_ are encoded with the following tags:

    InstrConfig('TABLE_GET', b'\x25', ['UnsignedInt', ], '#table.get'),
    InstrConfig('TABLE_SET', b'\x26', ['UnsignedInt', ], '#table.set'),
    InstrConfig('TABLE_INIT', b'\xFC\x0C', ['UnsignedInt', 'UnsignedInt', ], '#table.init'),
    InstrConfig('ELEM_DROP', b'\xFC\x0D', ['UnsignedInt', ], '#elem.drop'),
    InstrConfig('TABLE_COPY', b'\xFC\x0E', ['UnsignedInt', 'UnsignedInt', ], '#table.copy'),
    InstrConfig('TABLE_GROW', b'\xFC\x0F', ['UnsignedInt', ], '#table.grow'),
    InstrConfig('TABLE_SIZE', b'\xFC\x10', ['UnsignedInt', ], '#table.size'),
    InstrConfig('TABLE_FILL', b'\xFC\x11', ['UnsignedInt', ], '#table.fill'),

    # _Memory instructions_ are encoded with the following tags:

    InstrConfig('I32_LOAD', b'\x28', [constructor_arg('i32'), constructor_arg('load'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD', b'\x29', [constructor_arg('i64'), constructor_arg('load'), 'MemArg', ], '#load'),
    InstrConfig('F32_LOAD', b'\x2A', [constructor_arg('f32'), constructor_arg('load'), 'MemArg', ], '#load'),
    InstrConfig('F64_LOAD', b'\x2B', [constructor_arg('f64'), constructor_arg('load'), 'MemArg', ], '#load'),
    InstrConfig('I32_LOAD_8_S', b'\x2C', [constructor_arg('i32'), constructor_arg('load8_s'), 'MemArg', ], '#load'),
    InstrConfig('I32_LOAD_8_U', b'\x2D', [constructor_arg('i32'), constructor_arg('load8_u'), 'MemArg', ], '#load'),
    InstrConfig('I32_LOAD_16_S', b'\x2E', [constructor_arg('i32'), constructor_arg('load16_s'), 'MemArg', ], '#load'),
    InstrConfig('I32_LOAD_16_U', b'\x2F', [constructor_arg('i32'), constructor_arg('load16_u'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_8_S', b'\x30', [constructor_arg('i64'), constructor_arg('load8_s'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_8_U', b'\x31', [constructor_arg('i64'), constructor_arg('load8_u'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_16_S', b'\x32', [constructor_arg('i64'), constructor_arg('load16_s'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_16_U', b'\x33', [constructor_arg('i64'), constructor_arg('load16_u'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_32_S', b'\x34', [constructor_arg('i64'), constructor_arg('load32_s'), 'MemArg', ], '#load'),
    InstrConfig('I64_LOAD_32_U', b'\x35', [constructor_arg('i64'), constructor_arg('load32_u'), 'MemArg', ], '#load'),
    InstrConfig('I32_STORE', b'\x36', [constructor_arg('i32'), constructor_arg('store'), 'MemArg', ], '#store'),
    InstrConfig('I64_STORE', b'\x37', [constructor_arg('i64'), constructor_arg('store'), 'MemArg', ], '#store'),
    InstrConfig('F32_STORE', b'\x38', [constructor_arg('f32'), constructor_arg('store'), 'MemArg', ], '#store'),
    InstrConfig('F64_STORE', b'\x39', [constructor_arg('f64'), constructor_arg('store'), 'MemArg', ], '#store'),
    InstrConfig('I32_STORE_8', b'\x3A', [constructor_arg('i32'), constructor_arg('store8'), 'MemArg', ], '#store'),
    InstrConfig('I32_STORE_16', b'\x3B', [constructor_arg('i32'), constructor_arg('store16'), 'MemArg', ], '#store'),
    InstrConfig('I64_STORE_8', b'\x3C', [constructor_arg('i64'), constructor_arg('store8'), 'MemArg', ], '#store'),
    InstrConfig('I64_STORE_16', b'\x3D', [constructor_arg('i64'), constructor_arg('store16'), 'MemArg', ], '#store'),
    InstrConfig('I64_STORE_32', b'\x3E', [constructor_arg('i64'), constructor_arg('store32'), 'MemArg', ], '#store'),
    InstrConfig('MEM_SIZE', b'\x3F', [], 'memory.size'),
    InstrConfig('MEM_GROW', b'\x40', [], 'memory.grow'),
    InstrConfig('MEM_INIT', b'\xFC\x08', ['UnsignedInt', parse_constant(b'\x00'), ], not_implemented()),
    InstrConfig('DATA_DROP', b'\xFC\x09', ['UnsignedInt', ], not_implemented()),
    InstrConfig('MEM_COPY', b'\xFC\x0A', [parse_constant(b'\x00'), parse_constant(b'\x00'), ], 'memory.copy'),
    InstrConfig('MEM_FILL', b'\xFC\x0B', [parse_constant(b'\x00'), ], 'memory.fill'),

    # _Numeric instructions_ have the following tags:

    InstrConfig('I32_CONST', b'\x41', [constructor_arg('i32'), 'SignedInt', ], symbol('aIConst')),
    InstrConfig('I64_CONST', b'\x42', [constructor_arg('i64'), 'SignedInt', ], symbol('aIConst')),
    InstrConfig('F32_CONST', b'\x43', [constructor_arg('f32'), 'Float32', ], symbol('aFConst')),
    InstrConfig('F64_CONST', b'\x44', [constructor_arg('f64'), 'Float64', ], symbol('aFConst')),

    InstrConfig('I32_EQZ', b'\x45', [constructor_arg('i32'), constructor_arg('eqz'), ], symbol('aTestOp')),
    InstrConfig('I32_EQ', b'\x46', [constructor_arg('i32'), constructor_arg('eq'), ], symbol('aIRelOp')),
    InstrConfig('I32_NE', b'\x47', [constructor_arg('i32'), constructor_arg('ne'), ], symbol('aIRelOp')),
    InstrConfig('I32_LT_S', b'\x48', [constructor_arg('i32'), constructor_arg('lt_s'), ], symbol('aIRelOp')),
    InstrConfig('I32_LT_U', b'\x49', [constructor_arg('i32'), constructor_arg('lt_u'), ], symbol('aIRelOp')),
    InstrConfig('I32_GT_S', b'\x4A', [constructor_arg('i32'), constructor_arg('gt_s'), ], symbol('aIRelOp')),
    InstrConfig('I32_GT_U', b'\x4B', [constructor_arg('i32'), constructor_arg('gt_u'), ], symbol('aIRelOp')),
    InstrConfig('I32_LE_S', b'\x4C', [constructor_arg('i32'), constructor_arg('le_s'), ], symbol('aIRelOp')),
    InstrConfig('I32_LE_U', b'\x4D', [constructor_arg('i32'), constructor_arg('le_u'), ], symbol('aIRelOp')),
    InstrConfig('I32_GE_S', b'\x4E', [constructor_arg('i32'), constructor_arg('ge_s'), ], symbol('aIRelOp')),
    InstrConfig('I32_GE_U', b'\x4F', [constructor_arg('i32'), constructor_arg('ge_u'), ], symbol('aIRelOp')),

    InstrConfig('I64_EQZ', b'\x50', [constructor_arg('i64'), constructor_arg('eqz'), ], symbol('aTestOp')),
    InstrConfig('I64_EQ', b'\x51', [constructor_arg('i64'), constructor_arg('eq'), ], symbol('aIRelOp')),
    InstrConfig('I64_NE', b'\x52', [constructor_arg('i64'), constructor_arg('ne'), ], symbol('aIRelOp')),
    InstrConfig('I64_LT_S', b'\x53', [constructor_arg('i64'), constructor_arg('lt_s'), ], symbol('aIRelOp')),
    InstrConfig('I64_LT_U', b'\x54', [constructor_arg('i64'), constructor_arg('lt_u'), ], symbol('aIRelOp')),
    InstrConfig('I64_GT_S', b'\x55', [constructor_arg('i64'), constructor_arg('gt_s'), ], symbol('aIRelOp')),
    InstrConfig('I64_GT_U', b'\x56', [constructor_arg('i64'), constructor_arg('gt_u'), ], symbol('aIRelOp')),
    InstrConfig('I64_LE_S', b'\x57', [constructor_arg('i64'), constructor_arg('le_s'), ], symbol('aIRelOp')),
    InstrConfig('I64_LE_U', b'\x58', [constructor_arg('i64'), constructor_arg('le_u'), ], symbol('aIRelOp')),
    InstrConfig('I64_GE_S', b'\x59', [constructor_arg('i64'), constructor_arg('ge_s'), ], symbol('aIRelOp')),
    InstrConfig('I64_GE_U', b'\x5A', [constructor_arg('i64'), constructor_arg('ge_u'), ], symbol('aIRelOp')),

    InstrConfig('F32_EQ', b'\x5B', [constructor_arg('f32'), constructor_arg('eq'), ], symbol('aFRelOp')),
    InstrConfig('F32_NE', b'\x5C', [constructor_arg('f32'), constructor_arg('ne'), ], symbol('aFRelOp')),
    InstrConfig('F32_LT', b'\x5D', [constructor_arg('f32'), constructor_arg('lt'), ], symbol('aFRelOp')),
    InstrConfig('F32_GT', b'\x5E', [constructor_arg('f32'), constructor_arg('gt'), ], symbol('aFRelOp')),
    InstrConfig('F32_LE', b'\x5F', [constructor_arg('f32'), constructor_arg('le'), ], symbol('aFRelOp')),
    InstrConfig('F32_GE', b'\x60', [constructor_arg('f32'), constructor_arg('ge'), ], symbol('aFRelOp')),

    InstrConfig('F64_EQ', b'\x61', [constructor_arg('f64'), constructor_arg('eq'), ], symbol('aFRelOp')),
    InstrConfig('F64_NE', b'\x62', [constructor_arg('f64'), constructor_arg('ne'), ], symbol('aFRelOp')),
    InstrConfig('F64_LT', b'\x63', [constructor_arg('f64'), constructor_arg('lt'), ], symbol('aFRelOp')),
    InstrConfig('F64_GT', b'\x64', [constructor_arg('f64'), constructor_arg('gt'), ], symbol('aFRelOp')),
    InstrConfig('F64_LE', b'\x65', [constructor_arg('f64'), constructor_arg('le'), ], symbol('aFRelOp')),
    InstrConfig('F64_GE', b'\x66', [constructor_arg('f64'), constructor_arg('ge'), ], symbol('aFRelOp')),

    InstrConfig('I32_CLZ', b'\x67', [constructor_arg('i32'), constructor_arg('clz'), ], symbol('aIUnOp')),
    InstrConfig('I32_CTZ', b'\x68', [constructor_arg('i32'), constructor_arg('ctz'), ], symbol('aIUnOp')),
    InstrConfig('I32_POPCNT', b'\x69', [constructor_arg('i32'), constructor_arg('popcnt'), ], symbol('aIUnOp')),
    InstrConfig('I32_ADD', b'\x6A', [constructor_arg('i32'), constructor_arg('add'), ], symbol('aIBinOp')),
    InstrConfig('I32_SUB', b'\x6B', [constructor_arg('i32'), constructor_arg('sub'), ], symbol('aIBinOp')),
    InstrConfig('I32_MUL', b'\x6C', [constructor_arg('i32'), constructor_arg('mul'), ], symbol('aIBinOp')),
    InstrConfig('I32_DIV_S', b'\x6D', [constructor_arg('i32'), constructor_arg('div_s'), ], symbol('aIBinOp')),
    InstrConfig('I32_DIV_U', b'\x6E', [constructor_arg('i32'), constructor_arg('div_u'), ], symbol('aIBinOp')),
    InstrConfig('I32_REM_S', b'\x6F', [constructor_arg('i32'), constructor_arg('rem_s'), ], symbol('aIBinOp')),
    InstrConfig('I32_REM_U', b'\x70', [constructor_arg('i32'), constructor_arg('rem_u'), ], symbol('aIBinOp')),
    InstrConfig('I32_AND', b'\x71', [constructor_arg('i32'), constructor_arg('and'), ], symbol('aIBinOp')),
    InstrConfig('I32_OR', b'\x72', [constructor_arg('i32'), constructor_arg('or'), ], symbol('aIBinOp')),
    InstrConfig('I32_XOR', b'\x73', [constructor_arg('i32'), constructor_arg('xor'), ], symbol('aIBinOp')),
    InstrConfig('I32_SHL', b'\x74', [constructor_arg('i32'), constructor_arg('shl'), ], symbol('aIBinOp')),
    InstrConfig('I32_SHR_S', b'\x75', [constructor_arg('i32'), constructor_arg('shr_s'), ], symbol('aIBinOp')),
    InstrConfig('I32_SHR_U', b'\x76', [constructor_arg('i32'), constructor_arg('shr_u'), ], symbol('aIBinOp')),
    InstrConfig('I32_ROTL', b'\x77', [constructor_arg('i32'), constructor_arg('rotl'), ], symbol('aIBinOp')),
    InstrConfig('I32_ROTR', b'\x78', [constructor_arg('i32'), constructor_arg('rotr'), ], symbol('aIBinOp')),

    InstrConfig('I64_CLZ', b'\x79', [constructor_arg('i32'), constructor_arg('clz'), ], symbol('aIUnOp')),
    InstrConfig('I64_CTZ', b'\x7A', [constructor_arg('i32'), constructor_arg('ctz'), ], symbol('aIUnOp')),
    InstrConfig('I64_POPCNT', b'\x7B', [constructor_arg('i32'), constructor_arg('popcnt'), ], symbol('aIUnOp')),
    InstrConfig('I64_ADD', b'\x7C', [constructor_arg('i64'), constructor_arg('add'), ], symbol('aIBinOp')),
    InstrConfig('I64_SUB', b'\x7D', [constructor_arg('i64'), constructor_arg('sub'), ], symbol('aIBinOp')),
    InstrConfig('I64_MUL', b'\x7E', [constructor_arg('i64'), constructor_arg('mul'), ], symbol('aIBinOp')),
    InstrConfig('I64_DIV_S', b'\x7F', [constructor_arg('i64'), constructor_arg('div_s'), ], symbol('aIBinOp')),
    InstrConfig('I64_DIV_U', b'\x80', [constructor_arg('i64'), constructor_arg('div_u'), ], symbol('aIBinOp')),
    InstrConfig('I64_REM_S', b'\x81', [constructor_arg('i64'), constructor_arg('rem_s'), ], symbol('aIBinOp')),
    InstrConfig('I64_REM_U', b'\x82', [constructor_arg('i64'), constructor_arg('rem_u'), ], symbol('aIBinOp')),
    InstrConfig('I64_AND', b'\x83', [constructor_arg('i64'), constructor_arg('and'), ], symbol('aIBinOp')),
    InstrConfig('I64_OR', b'\x84', [constructor_arg('i64'), constructor_arg('or'), ], symbol('aIBinOp')),
    InstrConfig('I64_XOR', b'\x85', [constructor_arg('i64'), constructor_arg('xor'), ], symbol('aIBinOp')),
    InstrConfig('I64_SHL', b'\x86', [constructor_arg('i64'), constructor_arg('shl'), ], symbol('aIBinOp')),
    InstrConfig('I64_SHR_S', b'\x87', [constructor_arg('i64'), constructor_arg('shr_s'), ], symbol('aIBinOp')),
    InstrConfig('I64_SHR_U', b'\x88', [constructor_arg('i64'), constructor_arg('shr_u'), ], symbol('aIBinOp')),
    InstrConfig('I64_ROTL', b'\x89', [constructor_arg('i64'), constructor_arg('rotl'), ], symbol('aIBinOp')),
    InstrConfig('I64_ROTR', b'\x8A', [constructor_arg('i64'), constructor_arg('rotr'), ], symbol('aIBinOp')),

    InstrConfig('F32_ABS', b'\x8B', [constructor_arg('f32'), constructor_arg('abs'), ], symbol('aFUnOp')),
    InstrConfig('F32_NEG', b'\x8C', [constructor_arg('f32'), constructor_arg('neg'), ], symbol('aFUnOp')),
    InstrConfig('F32_CEIL', b'\x8D', [constructor_arg('f32'), constructor_arg('ceil'), ], symbol('aFUnOp')),
    InstrConfig('F32_FLOOR', b'\x8E', [constructor_arg('f32'), constructor_arg('floor'), ], symbol('aFUnOp')),
    InstrConfig('F32_TRUNC', b'\x8F', [constructor_arg('f32'), constructor_arg('trunc'), ], symbol('aFUnOp')),
    InstrConfig('F32_NEAREST', b'\x90', [constructor_arg('f32'), constructor_arg('nearest'), ], symbol('aFUnOp')),
    InstrConfig('F32_SQRT', b'\x91', [constructor_arg('f32'), constructor_arg('sqrt'), ], symbol('aFUnOp')),
    InstrConfig('F32_ADD', b'\x92', [constructor_arg('f32'), constructor_arg('add'), ], symbol('aFBinOp')),
    InstrConfig('F32_SUB', b'\x93', [constructor_arg('f32'), constructor_arg('sub'), ], symbol('aFBinOp')),
    InstrConfig('F32_MUL', b'\x94', [constructor_arg('f32'), constructor_arg('mul'), ], symbol('aFBinOp')),
    InstrConfig('F32_DIV', b'\x95', [constructor_arg('f32'), constructor_arg('div'), ], symbol('aFBinOp')),
    InstrConfig('F32_MIN', b'\x96', [constructor_arg('f32'), constructor_arg('min'), ], symbol('aFBinOp')),
    InstrConfig('F32_MAX', b'\x97', [constructor_arg('f32'), constructor_arg('max'), ], symbol('aFBinOp')),
    InstrConfig('F32_COPYSIGN', b'\x98', [constructor_arg('f32'), constructor_arg('copysign'), ], symbol('aFBinOp')),

    InstrConfig('F64_ABS', b'\x99', [constructor_arg('f64'), constructor_arg('abs'), ], symbol('aFUnOp')),
    InstrConfig('F64_NEG', b'\x9A', [constructor_arg('f64'), constructor_arg('neg'), ], symbol('aFUnOp')),
    InstrConfig('F64_CEIL', b'\x9B', [constructor_arg('f64'), constructor_arg('ceil'), ], symbol('aFUnOp')),
    InstrConfig('F64_FLOOR', b'\x9C', [constructor_arg('f64'), constructor_arg('floor'), ], symbol('aFUnOp')),
    InstrConfig('F64_TRUNC', b'\x9D', [constructor_arg('f64'), constructor_arg('trunc'), ], symbol('aFUnOp')),
    InstrConfig('F64_NEAREST', b'\x9E', [constructor_arg('f64'), constructor_arg('nearest'), ], symbol('aFUnOp')),
    InstrConfig('F64_SQRT', b'\x9F', [constructor_arg('f64'), constructor_arg('sqrt'), ], symbol('aFUnOp')),
    InstrConfig('F64_ADD', b'\xA0', [constructor_arg('f32'), constructor_arg('add'), ], symbol('aFBinOp')),
    InstrConfig('F64_SUB', b'\xA1', [constructor_arg('f32'), constructor_arg('sub'), ], symbol('aFBinOp')),
    InstrConfig('F64_MUL', b'\xA2', [constructor_arg('f32'), constructor_arg('mul'), ], symbol('aFBinOp')),
    InstrConfig('F64_DIV', b'\xA3', [constructor_arg('f32'), constructor_arg('div'), ], symbol('aFBinOp')),
    InstrConfig('F64_MIN', b'\xA4', [constructor_arg('f32'), constructor_arg('min'), ], symbol('aFBinOp')),
    InstrConfig('F64_MAX', b'\xA5', [constructor_arg('f32'), constructor_arg('max'), ], symbol('aFBinOp')),
    InstrConfig('F64_COPYSIGN', b'\xA6', [constructor_arg('f32'), constructor_arg('copysign'), ], symbol('aFBinOp')),

    InstrConfig('I32_WRAP_I64', b'\xA7', [constructor_arg('i32'), constructor_arg('wrap_i64'), ], symbol('aCvtOp')),
    InstrConfig('I32_TRUNC_F32_S', b'\xA8', [constructor_arg('i32'), constructor_arg('trunc_f32_s'), ], symbol('aCvtOp')),
    InstrConfig('I32_TRUNC_F32_U', b'\xA9', [constructor_arg('i32'), constructor_arg('trunc_f32_u'), ], symbol('aCvtOp')),
    InstrConfig('I32_TRUNC_F64_S', b'\xAA', [constructor_arg('i32'), constructor_arg('trunc_f64_s'), ], symbol('aCvtOp')),
    InstrConfig('I32_TRUNC_F64_U', b'\xAB', [constructor_arg('i32'), constructor_arg('trunc_f64_u'), ], symbol('aCvtOp')),

    InstrConfig('I64_EXTEND_I32_S', b'\xAC', [constructor_arg('i64'), constructor_arg('extend_i32_s'), ], symbol('aCvtOp')),
    InstrConfig('I64_EXTEND_I32_U', b'\xAD', [constructor_arg('i64'), constructor_arg('extend_i32_u'), ], symbol('aCvtOp')),
    InstrConfig('I64_TRUNC_F32_S', b'\xAE', [constructor_arg('i64'), constructor_arg('trunc_f32_s'), ], symbol('aCvtOp')),
    InstrConfig('I64_TRUNC_F32_U', b'\xAF', [constructor_arg('i64'), constructor_arg('trunc_f32_u'), ], symbol('aCvtOp')),
    InstrConfig('I64_TRUNC_F64_S', b'\xB0', [constructor_arg('i64'), constructor_arg('trunc_f64_s'), ], symbol('aCvtOp')),
    InstrConfig('I64_TRUNC_F64_U', b'\xB1', [constructor_arg('i64'), constructor_arg('trunc_f64_u'), ], symbol('aCvtOp')),

    InstrConfig('F32_CONVERT_I32_S', b'\xB2', [constructor_arg('f32'), constructor_arg('convert_i32_s'), ], symbol('aCvtOp')),
    InstrConfig('F32_CONVERT_I32_U', b'\xB3', [constructor_arg('f32'), constructor_arg('convert_i32_u'), ], symbol('aCvtOp')),
    InstrConfig('F32_CONVERT_I64_S', b'\xB4', [constructor_arg('f32'), constructor_arg('convert_i64_s'), ], symbol('aCvtOp')),
    InstrConfig('F32_CONVERT_I64_U', b'\xB5', [constructor_arg('f32'), constructor_arg('convert_i64_u'), ], symbol('aCvtOp')),
    InstrConfig('F32_DEMOTE_F64', b'\xB6', [constructor_arg('f32'), constructor_arg('demote_f64'), ], symbol('aCvtOp')),

    InstrConfig('F64_CONVERT_I32_S', b'\xB7', [constructor_arg('f64'), constructor_arg('convert_i32_s'), ], symbol('aCvtOp')),
    InstrConfig('F64_CONVERT_I32_U', b'\xB8', [constructor_arg('f64'), constructor_arg('convert_i32_u'), ], symbol('aCvtOp')),
    InstrConfig('F64_CONVERT_I64_S', b'\xB9', [constructor_arg('f64'), constructor_arg('convert_i64_s'), ], symbol('aCvtOp')),
    InstrConfig('F64_CONVERT_I64_U', b'\xBA', [constructor_arg('f64'), constructor_arg('convert_i64_u'), ], symbol('aCvtOp')),
    InstrConfig('F64_PROMOTE_F32', b'\xBB', [constructor_arg('f64'), constructor_arg('promote_f32'), ], symbol('aCvtOp')),

    InstrConfig('I32_REINTERPRET_F32', b'\xBC', [], not_implemented()),
    InstrConfig('I64_REINTERPRET_F64', b'\xBD', [], not_implemented()),
    InstrConfig('F32_REINTERPRET_I32', b'\xBE', [], not_implemented()),
    InstrConfig('F64_REINTERPRET_I64', b'\xBF', [], not_implemented()),

    InstrConfig('I32_EXTEND_8_S', b'\xC0', [constructor_arg('i32'), constructor_arg('extend8_s'), ], symbol('aExtendS')),
    InstrConfig('I32_EXTEND_16_S', b'\xC1', [constructor_arg('i32'), constructor_arg('extend16_s'), ], symbol('aExtendS')),
    InstrConfig('I64_EXTEND_8_S', b'\xC2', [constructor_arg('i64'), constructor_arg('extend8_s'), ], symbol('aExtendS')),
    InstrConfig('I64_EXTEND_16_S', b'\xC3', [constructor_arg('i64'), constructor_arg('extend16_s'), ], symbol('aExtendS')),
    InstrConfig('I64_EXTEND_32_S', b'\xC4', [constructor_arg('i64'), constructor_arg('extend32_s'), ], symbol('aExtendS')),

    InstrConfig('I32_TRUNC_SAT_F32_S', b'\xFC\x00', [], not_implemented()),
    InstrConfig('I32_TRUNC_SAT_F32_U', b'\xFC\x01', [], not_implemented()),
    InstrConfig('I32_TRUNC_SAT_F64_S', b'\xFC\x02', [], not_implemented()),
    InstrConfig('I32_TRUNC_SAT_F64_U', b'\xFC\x03', [], not_implemented()),
    InstrConfig('I64_TRUNC_SAT_F32_S', b'\xFC\x04', [], not_implemented()),
    InstrConfig('I64_TRUNC_SAT_F32_U', b'\xFC\x05', [], not_implemented()),
    InstrConfig('I64_TRUNC_SAT_F64_S', b'\xFC\x06', [], not_implemented()),
    InstrConfig('I64_TRUNC_SAT_F64_U', b'\xFC\x07', [], not_implemented()),

    # _Vector instructions_ have the following tags:

    InstrConfig('V128_LOAD', b'\xFD\x00', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_8X8_S', b'\xFD\x01', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_8X8_U', b'\xFD\x02', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_16X4_S', b'\xFD\x03', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_16X4_U', b'\xFD\x04', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_32X2_S', b'\xFD\x05', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_32X2_U', b'\xFD\x06', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_8_SPLAT', b'\xFD\x07', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_16_SPLAT', b'\xFD\x08', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_32_SPLAT', b'\xFD\x09', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_64_SPLAT', b'\xFD\x0A', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_32_ZERO', b'\xFD\x5C', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_64_ZERO', b'\xFD\x5D', ['MemArg', ], not_implemented()),
    InstrConfig('V128_STORE', b'\xFD\x0B', ['MemArg', ], not_implemented()),
    InstrConfig('V128_LOAD_8_LANE', b'\xFD\x54', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_LOAD_16_LANE', b'\xFD\x55', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_LOAD_32_LANE', b'\xFD\x56', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_LOAD_64_LANE', b'\xFD\x57', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_STORE_8_LANE', b'\xFD\x58', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_STORE_16_LANE', b'\xFD\x59', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_STORE_32_LANE', b'\xFD\x5A', ['MemArg', 'UnsignedInt', ], not_implemented()),
    InstrConfig('V128_STORE_64_LANE', b'\xFD\x5B', ['MemArg', 'UnsignedInt', ], not_implemented()),

    InstrConfig('V128_CONST_BYTES', b'\xFD\x0C', [repeated_bytes(16), ], not_implemented()),

    InstrConfig('I8X16_SHUFFLE', b'\xFD\x0D', [repeated_type('UnsignedInt', 16), ], not_implemented()),

    InstrConfig('I8X16_EXTRACT_LANE_S', b'\xFD\x15', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I8X16_EXTRACT_LANE_U', b'\xFD\x16', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I8X16_REPLACE_LANE', b'\xFD\x17', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I16X8_EXTRACT_LANE_S', b'\xFD\x18', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I16X8_EXTRACT_LANE_U', b'\xFD\x19', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I16X8_REPLACE_LANE', b'\xFD\x1A', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I32X4_EXTRACT_LANE', b'\xFD\x1B', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I32X4_REPLACE_LANE', b'\xFD\x1C', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I64X2_EXTRACT_LANE', b'\xFD\x1D', ['UnsignedInt', ], not_implemented()),
    InstrConfig('I64X2_REPLACE_LANE', b'\xFD\x1E', ['UnsignedInt', ], not_implemented()),
    InstrConfig('F32X4_EXTRACT_LANE', b'\xFD\x1F', ['UnsignedInt', ], not_implemented()),
    InstrConfig('F32X4_REPLACE_LANE', b'\xFD\x20', ['UnsignedInt', ], not_implemented()),
    InstrConfig('F64X2_EXTRACT_LANE', b'\xFD\x21', ['UnsignedInt', ], not_implemented()),
    InstrConfig('F64X2_REPLACE_LANE', b'\xFD\x22', ['UnsignedInt', ], not_implemented()),

    InstrConfig('I8X16_SWIZZLE', b'\xFD\x0E', [], not_implemented()),
    InstrConfig('I8X16_SPLAT', b'\xFD\x0F', [], not_implemented()),
    InstrConfig('I16X8_SPLAT', b'\xFD\x10', [], not_implemented()),
    InstrConfig('I32X4_SPLAT', b'\xFD\x11', [], not_implemented()),
    InstrConfig('I64X2_SPLAT', b'\xFD\x12', [], not_implemented()),
    InstrConfig('F32X4_SPLAT', b'\xFD\x13', [], not_implemented()),
    InstrConfig('F64X2_SPLAT', b'\xFD\x14', [], not_implemented()),

    InstrConfig('I8X16_EQ', b'\xFD\x23', [], not_implemented()),
    InstrConfig('I8X16_NE', b'\xFD\x24', [], not_implemented()),
    InstrConfig('I8X16_LT_S', b'\xFD\x25', [], not_implemented()),
    InstrConfig('I8X16_LT_U', b'\xFD\x26', [], not_implemented()),
    InstrConfig('I8X16_GT_S', b'\xFD\x27', [], not_implemented()),
    InstrConfig('I8X16_GT_U', b'\xFD\x28', [], not_implemented()),
    InstrConfig('I8X16_LE_S', b'\xFD\x29', [], not_implemented()),
    InstrConfig('I8X16_LE_U', b'\xFD\x2A', [], not_implemented()),
    InstrConfig('I8X16_GE_S', b'\xFD\x2B', [], not_implemented()),
    InstrConfig('I8X16_GE_U', b'\xFD\x2C', [], not_implemented()),

    InstrConfig('I16X8_EQ', b'\xFD\x2D', [], not_implemented()),
    InstrConfig('I16X8_NE', b'\xFD\x2E', [], not_implemented()),
    InstrConfig('I16X8_LT_S', b'\xFD\x2F', [], not_implemented()),
    InstrConfig('I16X8_LT_U', b'\xFD\x30', [], not_implemented()),
    InstrConfig('I16X8_GT_S', b'\xFD\x31', [], not_implemented()),
    InstrConfig('I16X8_GT_U', b'\xFD\x32', [], not_implemented()),
    InstrConfig('I16X8_LE_S', b'\xFD\x33', [], not_implemented()),
    InstrConfig('I16X8_LE_U', b'\xFD\x34', [], not_implemented()),
    InstrConfig('I16X8_GE_S', b'\xFD\x35', [], not_implemented()),
    InstrConfig('I16X8_GE_U', b'\xFD\x36', [], not_implemented()),

    InstrConfig('I32X4_EQ', b'\xFD\x37', [], not_implemented()),
    InstrConfig('I32X4_NE', b'\xFD\x38', [], not_implemented()),
    InstrConfig('I32X4_LT_S', b'\xFD\x39', [], not_implemented()),
    InstrConfig('I32X4_LT_U', b'\xFD\x3A', [], not_implemented()),
    InstrConfig('I32X4_GT_S', b'\xFD\x3B', [], not_implemented()),
    InstrConfig('I32X4_GT_U', b'\xFD\x3C', [], not_implemented()),
    InstrConfig('I32X4_LE_S', b'\xFD\x3D', [], not_implemented()),
    InstrConfig('I32X4_LE_U', b'\xFD\x3E', [], not_implemented()),
    InstrConfig('I32X4_GE_S', b'\xFD\x3F', [], not_implemented()),
    InstrConfig('I32X4_GE_U', b'\xFD\x40', [], not_implemented()),

    InstrConfig('I64X2_EQ', b'\xFD\xD6\x01', [], not_implemented()),
    InstrConfig('I64X2_NE', b'\xFD\xD7\x01', [], not_implemented()),
    InstrConfig('I64X2_LT_S', b'\xFD\xD8\x01', [], not_implemented()),
    InstrConfig('I64X2_GT_S', b'\xFD\xD9\x01', [], not_implemented()),
    InstrConfig('I64X2_LE_S', b'\xFD\xDA\x01', [], not_implemented()),
    InstrConfig('I64X2_GE_S', b'\xFD\xDB\x01', [], not_implemented()),

    InstrConfig('F32X4_EQ', b'\xFD\x41', [], not_implemented()),
    InstrConfig('F32X4_NE', b'\xFD\x42', [], not_implemented()),
    InstrConfig('F32X4_LT', b'\xFD\x43', [], not_implemented()),
    InstrConfig('F32X4_GT', b'\xFD\x44', [], not_implemented()),
    InstrConfig('F32X4_LE', b'\xFD\x45', [], not_implemented()),
    InstrConfig('F32X4_GE', b'\xFD\x46', [], not_implemented()),

    InstrConfig('F64X2_EQ', b'\xFD\x47', [], not_implemented()),
    InstrConfig('F64X2_NE', b'\xFD\x48', [], not_implemented()),
    InstrConfig('F64X2_LT', b'\xFD\x49', [], not_implemented()),
    InstrConfig('F64X2_GT', b'\xFD\x4A', [], not_implemented()),
    InstrConfig('F64X2_LE', b'\xFD\x4B', [], not_implemented()),
    InstrConfig('F64X2_GE', b'\xFD\x4C', [], not_implemented()),

    InstrConfig('V128_NOT', b'\xFD\x4D', [], not_implemented()),
    InstrConfig('V128_AND', b'\xFD\x4E', [], not_implemented()),
    InstrConfig('V128_ANDNOT', b'\xFD\x4F', [], not_implemented()),
    InstrConfig('V128_OR', b'\xFD\x50', [], not_implemented()),
    InstrConfig('V128_XOR', b'\xFD\x51', [], not_implemented()),
    InstrConfig('V128_BITSELECT', b'\xFD\x52', [], not_implemented()),
    InstrConfig('V128_ANY_TRUE', b'\xFD\x53', [], not_implemented()),

    InstrConfig('I8X16_ABS', b'\xFD\x60', [], not_implemented()),
    InstrConfig('I8X16_NEG', b'\xFD\x61', [], not_implemented()),
    InstrConfig('I8X16_POPCNT', b'\xFD\x62', [], not_implemented()),
    InstrConfig('I8X16_ALL_TRUE', b'\xFD\x63', [], not_implemented()),
    InstrConfig('I8X16_BITMASK', b'\xFD\x64', [], not_implemented()),
    InstrConfig('I8X16_NARROW_I16X8_S', b'\xFD\x65', [], not_implemented()),
    InstrConfig('I8X16_NARROW_I16X8_U', b'\xFD\x66', [], not_implemented()),
    InstrConfig('I8X16_SHL', b'\xFD\x6B', [], not_implemented()),
    InstrConfig('I8X16_SHR_S', b'\xFD\x6C', [], not_implemented()),
    InstrConfig('I8X16_SHR_U', b'\xFD\x6D', [], not_implemented()),
    InstrConfig('I8X16_ADD', b'\xFD\x6E', [], not_implemented()),
    InstrConfig('I8X16_ADD_SAT_S', b'\xFD\x6F', [], not_implemented()),
    InstrConfig('I8X16_ADD_SAT_U', b'\xFD\x70', [], not_implemented()),
    InstrConfig('I8X16_SUB', b'\xFD\x71', [], not_implemented()),
    InstrConfig('I8X16_SUB_SAT_S', b'\xFD\x72', [], not_implemented()),
    InstrConfig('I8X16_SUB_SAT_U', b'\xFD\x73', [], not_implemented()),
    InstrConfig('I8X16_MIN_S', b'\xFD\x76', [], not_implemented()),
    InstrConfig('I8X16_MIN_U', b'\xFD\x77', [], not_implemented()),
    InstrConfig('I8X16_MAX_S', b'\xFD\x78', [], not_implemented()),
    InstrConfig('I8X16_MAX_U', b'\xFD\x79', [], not_implemented()),
    InstrConfig('I8X16_AVGR_U', b'\xFD\x7B', [], not_implemented()),

    InstrConfig('I16X8_EXTADD_PAIRWISE_I8X16_S', b'\xFD\x7C', [], not_implemented()),
    InstrConfig('I16X8_EXTADD_PAIRWISE_I8X16_U', b'\xFD\x7D', [], not_implemented()),
    InstrConfig('I16X8_ABS', b'\xFD\x80\x01', [], not_implemented()),
    InstrConfig('I16X8_NEG', b'\xFD\x81\x01', [], not_implemented()),
    InstrConfig('I16X8_Q15MULR_SAT_S', b'\xFD\x82\x01', [], not_implemented()),
    InstrConfig('I16X8_ALL_TRUE', b'\xFD\x83\x01', [], not_implemented()),
    InstrConfig('I16X8_BITMASK', b'\xFD\x84\x01', [], not_implemented()),
    InstrConfig('I16X8_NARROW_I32X4_S', b'\xFD\x85\x01', [], not_implemented()),
    InstrConfig('I16X8_NARROW_I32X4_U', b'\xFD\x86\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTEND_LOW_I8X16_S', b'\xFD\x87\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTEND_HIGH_I8X16_S', b'\xFD\x88\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTEND_LOW_I8X16_U', b'\xFD\x89\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTEND_HIGH_I8X16_U', b'\xFD\x8A\x01', [], not_implemented()),
    InstrConfig('I16X8_SHL', b'\xFD\x8B\x01', [], not_implemented()),
    InstrConfig('I16X8_SHR_S', b'\xFD\x8C\x01', [], not_implemented()),
    InstrConfig('I16X8_SHR_U', b'\xFD\x8D\x01', [], not_implemented()),
    InstrConfig('I16X8_ADD', b'\xFD\x8E\x01', [], not_implemented()),
    InstrConfig('I16X8_ADD_SAT_S', b'\xFD\x8F\x01', [], not_implemented()),
    InstrConfig('I16X8_ADD_SAT_U', b'\xFD\x90\x01', [], not_implemented()),
    InstrConfig('I16X8_SUB', b'\xFD\x91\x01', [], not_implemented()),
    InstrConfig('I16X8_SUB_SAT_S', b'\xFD\x92\x01', [], not_implemented()),
    InstrConfig('I16X8_SUB_SAT_U', b'\xFD\x93\x01', [], not_implemented()),
    InstrConfig('I16X8_MUL', b'\xFD\x95\x01', [], not_implemented()),
    InstrConfig('I16X8_MIN_S', b'\xFD\x96\x01', [], not_implemented()),
    InstrConfig('I16X8_MIN_U', b'\xFD\x97\x01', [], not_implemented()),
    InstrConfig('I16X8_MAX_S', b'\xFD\x98\x01', [], not_implemented()),
    InstrConfig('I16X8_MAX_U', b'\xFD\x99\x01', [], not_implemented()),
    InstrConfig('I16X8_AVGR_U', b'\xFD\x9B\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTMUL_LOW_I8X16_S', b'\xFD\x9C\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTMUL_HIGH_I8X16_S', b'\xFD\x9D\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTMUL_LOW_I8X16_U', b'\xFD\x9E\x01', [], not_implemented()),
    InstrConfig('I16X8_EXTMUL_HIGH_I8X16_U', b'\xFD\x9F\x01', [], not_implemented()),

    InstrConfig('I32X4_EXTADD_PAIRWISE_I16X8_S', b'\xFD\x7E', [], not_implemented()),
    InstrConfig('I32X4_EXTADD_PAIRWISE_I16X8_U', b'\xFD\x7F', [], not_implemented()),
    InstrConfig('I32X4_ABS', b'\xFD\xA0\x01', [], not_implemented()),
    InstrConfig('I32X4_NEG', b'\xFD\xA1\x01', [], not_implemented()),
    InstrConfig('I32X4_ALL_TRUE', b'\xFD\xA3\x01', [], not_implemented()),
    InstrConfig('I32X4_BITMASK', b'\xFD\xA4\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTEND_LOW_I16X8_S', b'\xFD\xA7\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTEND_HIGH_I16X8_S', b'\xFD\xA8\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTEND_LOW_I16X8_U', b'\xFD\xA9\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTEND_HIGH_I16X8_U', b'\xFD\xAA\x01', [], not_implemented()),
    InstrConfig('I32X4_SHL', b'\xFD\xAB\x01', [], not_implemented()),
    InstrConfig('I32X4_SHR_S', b'\xFD\xAC\x01', [], not_implemented()),
    InstrConfig('I32X4_SHR_U', b'\xFD\xAD\x01', [], not_implemented()),
    InstrConfig('I32X4_ADD', b'\xFD\xAE\x01', [], not_implemented()),
    InstrConfig('I32X4_SUB', b'\xFD\xB1\x01', [], not_implemented()),
    InstrConfig('I32X4_MUL', b'\xFD\xB5\x01', [], not_implemented()),
    InstrConfig('I32X4_MIN_S', b'\xFD\xB6\x01', [], not_implemented()),
    InstrConfig('I32X4_MIN_U', b'\xFD\xB7\x01', [], not_implemented()),
    InstrConfig('I32X4_MAX_S', b'\xFD\xB8\x01', [], not_implemented()),
    InstrConfig('I32X4_MAX_U', b'\xFD\xB9\x01', [], not_implemented()),
    InstrConfig('I32X4_DOT_I16X8_S', b'\xFD\xBA\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTMUL_LOW_I16X8_S', b'\xFD\xBC\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTMUL_HIGH_I16X8_S', b'\xFD\xBD\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTMUL_LOW_I16X8_U', b'\xFD\xBE\x01', [], not_implemented()),
    InstrConfig('I32X4_EXTMUL_HIGH_I16X8_U', b'\xFD\xBF\x01', [], not_implemented()),

    InstrConfig('I64X2_ABS', b'\xFD\xC0\x01', [], not_implemented()),
    InstrConfig('I64X2_NEG', b'\xFD\xC1\x01', [], not_implemented()),
    InstrConfig('I64X2_ALL_TRUE', b'\xFD\xC3\x01', [], not_implemented()),
    InstrConfig('I64X2_BITMASK', b'\xFD\xC4\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTEND_LOW_I32X4_S', b'\xFD\xC7\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTEND_HIGH_I32X4_S', b'\xFD\xC8\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTEND_LOW_I32X4_U', b'\xFD\xC9\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTEND_HIGH_I32X4_U', b'\xFD\xCA\x01', [], not_implemented()),
    InstrConfig('I64X2_SHL', b'\xFD\xCB\x01', [], not_implemented()),
    InstrConfig('I64X2_SHR_S', b'\xFD\xCC\x01', [], not_implemented()),
    InstrConfig('I64X2_SHR_U', b'\xFD\xCD\x01', [], not_implemented()),
    InstrConfig('I64X2_ADD', b'\xFD\xCE\x01', [], not_implemented()),
    InstrConfig('I64X2_SUB', b'\xFD\xD1\x01', [], not_implemented()),
    InstrConfig('I64X2_MUL', b'\xFD\xD5\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTMUL_LOW_I32X4_S', b'\xFD\xDC\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTMUL_HIGH_I32X4_S', b'\xFD\xDD\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTMUL_LOW_I32X4_U', b'\xFD\xDE\x01', [], not_implemented()),
    InstrConfig('I64X2_EXTMUL_HIGH_I32X4_U', b'\xFD\xDF\x01', [], not_implemented()),

    InstrConfig('F32X4_CEIL', b'\xFD\x67', [], not_implemented()),
    InstrConfig('F32X4_FLOOR', b'\xFD\x68', [], not_implemented()),
    InstrConfig('F32X4_TRUNC', b'\xFD\x69', [], not_implemented()),
    InstrConfig('F32X4_NEAREST', b'\xFD\x6A', [], not_implemented()),
    InstrConfig('F32X4_ABS', b'\xFD\xE0\x01', [], not_implemented()),
    InstrConfig('F32X4_NEG', b'\xFD\xE1\x01', [], not_implemented()),
    InstrConfig('F32X4_SQRT', b'\xFD\xE3\x01', [], not_implemented()),
    InstrConfig('F32X4_ADD', b'\xFD\xE4\x01', [], not_implemented()),
    InstrConfig('F32X4_SUB', b'\xFD\xE5\x01', [], not_implemented()),
    InstrConfig('F32X4_MUL', b'\xFD\xE6\x01', [], not_implemented()),
    InstrConfig('F32X4_DIV', b'\xFD\xE7\x01', [], not_implemented()),
    InstrConfig('F32X4_MIN', b'\xFD\xE8\x01', [], not_implemented()),
    InstrConfig('F32X4_MAX', b'\xFD\xE9\x01', [], not_implemented()),
    InstrConfig('F32X4_PMIN', b'\xFD\xEA\x01', [], not_implemented()),
    InstrConfig('F32X4_PMAX', b'\xFD\xEB\x01', [], not_implemented()),

    InstrConfig('F64X2_CEIL', b'\xFD\x74', [], not_implemented()),
    InstrConfig('F64X2_FLOOR', b'\xFD\x75', [], not_implemented()),
    InstrConfig('F64X2_TRUNC', b'\xFD\x7A', [], not_implemented()),
    InstrConfig('F64X2_NEAREST', b'\xFD\x94\x01', [], not_implemented()),
    InstrConfig('F64X2_ABS', b'\xFD\xEC\x01', [], not_implemented()),
    InstrConfig('F64X2_NEG', b'\xFD\xED\x01', [], not_implemented()),
    InstrConfig('F64X2_SQRT', b'\xFD\xEF\x01', [], not_implemented()),
    InstrConfig('F64X2_ADD', b'\xFD\xF0\x01', [], not_implemented()),
    InstrConfig('F64X2_SUB', b'\xFD\xF1\x01', [], not_implemented()),
    InstrConfig('F64X2_MUL', b'\xFD\xF2\x01', [], not_implemented()),
    InstrConfig('F64X2_DIV', b'\xFD\xF3\x01', [], not_implemented()),
    InstrConfig('F64X2_MIN', b'\xFD\xF4\x01', [], not_implemented()),
    InstrConfig('F64X2_MAX', b'\xFD\xF5\x01', [], not_implemented()),
    InstrConfig('F64X2_PMIN', b'\xFD\xF6\x01', [], not_implemented()),
    InstrConfig('F64X2_PMAX', b'\xFD\xF7\x01', [], not_implemented()),

    InstrConfig('I32X4_TRUNC_SAT_F32X4_S', b'\xFD\xF8\x01', [], not_implemented()),
    InstrConfig('I32X4_TRUNC_SAT_F32X4_U', b'\xFD\xF9\x01', [], not_implemented()),
    InstrConfig('F32X4_CONVERT_I32X4_S', b'\xFD\xFA\x01', [], not_implemented()),
    InstrConfig('F32X4_CONVERT_I32X4_U', b'\xFD\xFB\x01', [], not_implemented()),
    InstrConfig('I32X4_TRUNC_SAT_F64X2_S_ZERO', b'\xFD\xFC\x01', [], not_implemented()),
    InstrConfig('I32X4_TRUNC_SAT_F64X2_U_ZERO', b'\xFD\xFD\x01', [], not_implemented()),
    InstrConfig('F64X2_CONVERT_LOW_I32X4_S', b'\xFD\xFE\x01', [], not_implemented()),
    InstrConfig('F64X2_CONVERT_LOW_I32X4_U', b'\xFD\xFF\x01', [], not_implemented()),
    InstrConfig('F32X4_DEMOTE_F64X2_ZERO', b'\xFD\x5E', [], not_implemented()),
    InstrConfig('F64X2_PROMOTE_LOW_F32X4', b'\xFD\x5F', [], not_implemented()),
]
# fmt: on


def parse_single_item(parser_prefix: str, item: InstrConfig, output_pieces: list[str]) -> None:
    current_prefix = parser_prefix
    if item.prefix:
        current_prefix = parser_prefix + 'xbytes'
        output_pieces.append(
            f"""
  syntax InstrResult  ::= {parser_prefix}(BytesWithIndex)  [function, total]
                        | #{parser_prefix}(BytesWithIndexOrError)  [function, total]
  rule {parser_prefix}(BWI:BytesWithIndex) => #{parser_prefix}(parseConstant(BWI, {bytes_to_k(item.prefix)}))
  rule #{parser_prefix}(BWI:BytesWithIndex) => {current_prefix}(BWI)
  rule #{parser_prefix}(E:ParseError) => E

"""
        )

    output_pieces.append(f'  syntax InstrResult ::= {current_prefix}(BytesWithIndex)  [function, total]\n')
    # Argument parsing
    parsing_args = [arg for arg in item.args if arg.is_parsing_arg()]
    suffix = 1
    lhs_function = current_prefix
    prev_args: list[tuple[int, Argument]] = []
    last_parsed = None
    for i, arg in enumerate(item.args):
        if not arg.is_parsing_arg():
            continue

        rhs_function = f'#{current_prefix}s{suffix}'
        suffix += 1

        output_pieces.append(
            f"""  syntax InstrResult ::= {rhs_function}
                            ( """
        )
        newline_indented_comma = """
                            , """
        newline_indented_declaration_end = """
                            )  [function, total]
"""
        first = True
        for _, prev in prev_args:
            if first:
                first = False
            else:
                output_pieces.append(newline_indented_comma)
            output_pieces.append(prev.value_type())
        if last_parsed:
            _, parsed_arg = last_parsed
            if first:
                first = False
            else:
                output_pieces.append(newline_indented_comma)
            output_pieces.append(f'{parsed_arg.value_type()}')
        if first:
            first = False
        else:
            output_pieces.append(newline_indented_comma)
        output_pieces.append(f'{arg.result_type()}')
        output_pieces.append(newline_indented_declaration_end)

        # Success rewrite rule
        lhs_args = []
        rhs_args = []
        for i, prev in prev_args:
            lhs_args.append(prev.lhs_argument(i, unused=False))
            rhs_args.append(prev.rhs_argument(i, False))
        if last_parsed:
            parsed_arg_idx, parsed_arg = last_parsed
            lhs_args.append(f'{parsed_arg.result_argument(parsed_arg_idx, "BWI")}')
            rhs_args.append(f'{parsed_arg.rhs_argument(parsed_arg_idx, False)}')
        else:
            lhs_args.append('BWI')
        rhs_args.append(arg.parser('BWI'))
        output_pieces.append(f'  rule {lhs_function}({", ".join(lhs_args)}) => {rhs_function}({", ".join(rhs_args)})\n')

        if suffix > 2:
            # Failure rewrite rule for every lhs_function except the first one.
            failure_lhs_args = []
            for i, prev in prev_args:
                failure_lhs_args.append(prev.lhs_argument(i, unused=True))
            failure_lhs_args.append('E:ParseError')
            output_pieces.append(f'  rule {lhs_function}({", ".join(failure_lhs_args)}) => E\n')

        # Update data
        if last_parsed:
            prev_args.append(last_parsed)
        lhs_function = rhs_function

        if arg.is_used_in_constructor():
            last_parsed = (i, arg)
        else:
            last_parsed = None

    # Result construction
    result_lhs_args = []
    for prev_index, prev_arg in prev_args:
        result_lhs_args.append(prev_arg.lhs_argument(prev_index, unused=False))
    if last_parsed:
        result_lhs_args.append(arg.result_argument(i, 'BWI' if item.constructor.needs_bwi() else '_BWI'))
    else:
        result_lhs_args.append('BWI:BytesWithIndex')
    output_pieces.append(f'  rule {lhs_function}({", ".join(result_lhs_args)}) => ')
    item.constructor.build(item.args, 'BWI', output_pieces)
    output_pieces.append('\n')

    if parsing_args:
        # Error handling
        error_lhs_args = []
        for prev_index, prev_arg in prev_args:
            error_lhs_args.append(prev_arg.lhs_argument(prev_index, unused=True))
        error_lhs_args.append('E:ParseError')
        output_pieces.append(f'  rule {lhs_function}({", ".join(error_lhs_args)}) => E\n')


def parse_group(parser_prefix: str, items: list[InstrConfig], output_pieces: list[str]) -> None:
    assert items
    if len(items) == 1:
        parse_single_item(parser_prefix, items[0], output_pieces)
    else:
        output_pieces.append(f'  syntax InstrResult ::= {parser_prefix}(BytesWithIndex)  [function, total]\n')
        parse_rules(parser_prefix, items, output_pieces)


def parse_rules(parser_prefix: str, items: list[InstrConfig], output_pieces: list[str]) -> None:
    assert items
    output_pieces.append(
        f"""
  syntax InstrResult ::= #{parser_prefix}p1(IntResult)  [function, total]
                       | #{parser_prefix}p2(Int, BytesWithIndex)  [function, total]
  rule {parser_prefix}(BWI:BytesWithIndex) => #{parser_prefix}p1(parseByteAsInt(BWI))
  rule #{parser_prefix}p1(intResult(I:Int, BWI:BytesWithIndex)) => #{parser_prefix}p2(I, BWI)
  rule #{parser_prefix}p1(E:ParseError) => E
"""
    )

    groups: list[list[InstrConfig]] = [[] for _ in range(256)]
    for instr in items:
        assert len(instr.prefix) > 0
        first_prefix = instr.prefix[0]
        assert 0 <= first_prefix and first_prefix < 256
        groups[first_prefix].append(instr.with_prefix(instr.prefix[1:]))
    for i in range(256):
        if not groups[i]:
            continue
        output_pieces.append(f'  rule #{parser_prefix}p2({i}, BWI:BytesWithIndex) => {parser_prefix}x{i}(BWI)\n')
    output_pieces.append(
        f'  rule #{parser_prefix}p2(I:Int, bwi(B:Bytes, Index:Int)) => parseError("#{parser_prefix}p2", ListItem(I) ListItem(Index) ListItem(lengthBytes(B)) ListItem(B))  [owise]\n'
    )
    output_pieces.append('\n')
    for i in range(256):
        if not groups[i]:
            continue
        parse_group(f'{parser_prefix}x{i}', groups[i], output_pieces)


def main() -> None:
    output_pieces = [
        f"""This was generated by `{os.path.basename(__file__)}`. Do not edit this file directly.

```k
module BINARY-PARSER-INSTR-SYNTAX
  imports BINARY-PARSER-BASE-SYNTAX
  imports WASM-COMMON-SYNTAX

  syntax BinaryInstr ::= Instr

  syntax InstrResult ::= instrResult(BinaryInstr, BytesWithIndex) | ParseError
  syntax InstrResult ::= parseInstr(BytesWithIndex)  [function, total]

  syntax InstrOrError ::= Instr | ParseError
endmodule

module BINARY-PARSER-INSTR
  imports BINARY-PARSER-BLOCK-SYNTAX
  imports BINARY-PARSER-BYTES-SYNTAX
  imports BINARY-PARSER-CONSTANT-SYNTAX
  imports BINARY-PARSER-FLOAT-SYNTAX
  imports BINARY-PARSER-HELPERS-SYNTAX
  imports BINARY-PARSER-IF-SYNTAX
  imports BINARY-PARSER-INSTR-SYNTAX
  imports BINARY-PARSER-INT-SYNTAX
  imports BINARY-PARSER-LOOP-SYNTAX
  imports BINARY-PARSER-MEMARG-SYNTAX
  imports BINARY-PARSER-VALTYPE-SYNTAX
  imports WASM

""",
    ]
    parse_rules('parseInstr', INSTRS_CONFIG, output_pieces)
    output_pieces.append('endmodule\n')
    output_pieces.append('```\n')
    print(''.join(output_pieces))


if __name__ == '__main__':
    main()
