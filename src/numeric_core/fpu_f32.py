# src/numeric_core/fpu_f32.py
from typing import Dict, Tuple
from .bits import Bits, to_uint
from .adders import add
from .shifter import sll, srl
from .twos import decode_twos_complement

WIDTH = 32

# pack fields into IEEE-754 float32
def pack_f32(sign: int, exp: int, frac: int) -> Bits:
    v = (sign << 31) | ((exp & 0xFF) << 23) | (frac & 0x7FFFFF)
    out: Bits = []
    for i in range(31, -1, -1):
        out.append('1' if (v >> i) & 1 else '0')
    return out

# unpack IEEE-754 float32 fields
def unpack_f32(bits: Bits) -> Tuple[int, int, int]:
    v = to_uint(bits)
    sign = (v >> 31) & 1
    exp = (v >> 23) & 0xFF
    frac = v & 0x7FFFFF
    return sign, exp, frac

# add two float32 values
# AI-BEGIN
def fadd(a: Bits, b: Bits) -> Bits:
    sa, ea, fa = unpack_f32(a)
    sb, eb, fb = unpack_f32(b)

    # implicit leading 1 for normals
    if ea != 0:
        fa |= (1 << 23)
    if eb != 0:
        fb |= (1 << 23)

    # align exponents
    if ea > eb:
        shift = ea - eb
        fb >>= shift
        exp = ea
    else:
        shift = eb - ea
        fa >>= shift
        exp = eb

    # add or subtract mantissas
    if sa == sb:
        mant = fa + fb
        sign = sa
    else:
        if fa >= fb:
            mant = fa - fb
            sign = sa
        else:
            mant = fb - fa
            sign = sb

    # normalize if needed
    if mant == 0:
        return pack_f32(0, 0, 0)

    # renormalize left
    while mant >= (1 << 24):
        mant >>= 1
        exp += 1

    # renormalize right
    while mant < (1 << 23) and exp > 0:
        mant <<= 1
        exp -= 1

    frac = mant & 0x7FFFFF
    return pack_f32(sign, exp, frac)
# AI-END

# subtract b from a
def fsub(a: Bits, b: Bits) -> Bits:
    sb, eb, fb = unpack_f32(b)
    # flip sign bit of b, pack again
    bneg = pack_f32(sb ^ 1, eb, fb)
    return fadd(a, bneg)

# multiply two float32 values
# AI-BEGIN
def fmul(a: Bits, b: Bits) -> Bits:
    sa, ea, fa = unpack_f32(a)
    sb, eb, fb = unpack_f32(b)

    # implicit leading 1 for normals
    if ea != 0:
        fa |= (1 << 23)
    if eb != 0:
        fb |= (1 << 23)

    sign = sa ^ sb
    exp = ea + eb - 127

    # 24-bit × 24-bit mantissa
    prod = fa * fb

    # normalize: product is 48 bits, leading bit around bit 47 or 46
    if (prod >> 47) == 1:
        mant = prod >> 24
        exp += 1
    else:
        mant = prod >> 23

    # handle underflow
    if exp <= 0:
        return pack_f32(sign, 0, 0)

    # handle overflow
    if exp >= 255:
        return pack_f32(sign, 0xFF, 0)

    frac = mant & 0x7FFFFF
    return pack_f32(sign, exp, frac)
# AI-END
