# src/numeric_core/bits.py
# AI-BEGIN: helper primitives
from typing import List, Tuple


Bit = str # '0' or '1'
Bits = List[Bit]


def zpad(bits: Bits, width: int) -> Bits:
    if len(bits) >= width:
        return bits[-width:]
    return ['0'] * (width - len(bits)) + bits


def ones(width: int) -> Bits:
    return ['1'] * width


def zeros(width: int) -> Bits:
    return ['0'] * width


def from_uint(n: int, width: int) -> Bits:
    # Only used in tests OR when n was built from bits already; not in arithmetic.
    # Converts by repeated division by 2 using string logic? Simpler: assume n>=0 only for scaffolding.
    out: Bits = []
    if n == 0:
        out = ['0']
    else:
        x = n
        while x > 0:
            out.append('1' if (x & 1) == 1 else '0')
            x //= 2
        out.reverse()
    return zpad(out, width)


def to_uint(bits: Bits) -> int:
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b == '1' else 0)
    return v


def pretty_bin32(bits: Bits) -> str:
    s = ''.join(bits)
    # group into 8 nibbles with underscores
    return '_'.join(s[i:i+8] for i in range(0, 32, 8))


_HEX = {
'0000':'0','0001':'1','0010':'2','0011':'3',
'0100':'4','0101':'5','0110':'6','0111':'7',
'1000':'8','1001':'9','1010':'A','1011':'B',
'1100':'C','1101':'D','1110':'E','1111':'F',
}


def to_hex32(bits: Bits) -> str:
    s = ''.join(bits)
    # ensure multiple of 4
    if len(s) % 4 != 0:
        s = ('0' * (4 - (len(s) % 4))) + s
    hex_chars = []
    for i in range(0, len(s), 4):
        hex_chars.append(_HEX[s[i:i+4]])
    # zero pad to 8 nibbles
    while len(hex_chars) < 8:
        hex_chars.insert(0, '0')
    return '0x' + ''.join(hex_chars)
# AI-END