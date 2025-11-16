# src/numeric_core/twos.py
from typing import Dict
from .bits import Bits, zpad, to_hex32, pretty_bin32
from .adders import negate, invert, add

WIDTH = 32
MIN = -(2 ** (WIDTH - 1))
MAX = (2 ** (WIDTH - 1)) - 1

# AI-BEGIN
def encode_twos_complement(value: int) -> Dict[str, object]:
    overflow = 0
    if value < MIN or value > MAX:
        overflow = 1
        # wrap into 32-bit range; overflow flag tells the story
        if value < 0:
            value = (value + (1 << 32)) % (1 << 32)
        else:
            value = value % (1 << 32)

    # build magnitude in bits (no bin())
    v = value
    if v < 0:
        v = -v

    mag: Bits = []
    if v == 0:
        mag = ['0']
    else:
        x = v
        while x > 0:
            mag.append('1' if (x & 1) == 1 else '0')
            x //= 2
        mag.reverse()

    mag = zpad(mag, WIDTH)

    # for negative values, store two's complement
    if value < 0:
        mag = negate(mag)

    return {
        'bin': pretty_bin32(mag),
        'hex': to_hex32(mag),
        'overflow_flag': overflow,
        'bits': mag,
    }

# decode 32-bit two's complement bits -> signed int
def decode_twos_complement(bits: Bits) -> Dict[str, int]:
    assert len(bits) == WIDTH

    # positive: just convert bits to int
    if bits[0] == '0':
        val = 0
        for b in bits:
            val = (val << 1) | (1 if b == '1' else 0)
        return {'value': val}

    # negative: take two's complement to get magnitude
    inv = invert(bits)
    one = ['0'] * (WIDTH - 1) + ['1']
    mag, _ = add(inv, one)

    val = 0
    for b in mag:
        val = (val << 1) | (1 if b == '1' else 0)
    return {'value': -val}
# AI-END

# sign-extend a bit-vector to a wider width
def sign_extend(bits: Bits, new_width: int) -> Bits:
    assert new_width >= len(bits)
    s = bits[0]
    return [s] * (new_width - len(bits)) + bits

# zero-extend a bit-vector to a wider width
def zero_extend(bits: Bits, new_width: int) -> Bits:
    assert new_width >= len(bits)
    return ['0'] * (new_width - len(bits)) + bits
