# src/numeric_core/adders.py
from typing import Tuple, List

Bit = str          # a single bit: '0' or '1'
Bits = List[Bit]   # a list of bits

# Half adder: adds two bits
def h_add(a: Bit, b: Bit) -> Tuple[Bit, Bit]:
    s = '1' if a != b else '0'
    c = '1' if (a == '1' and b == '1') else '0'
    return s, c

# Full adder: adds two bits plus a carry-in, returns (sum, carry_out)
def f_add(a: Bit, b: Bit, cin: Bit) -> Tuple[Bit, Bit]:
    s1, c1 = h_add(a, b)
    s2, c2 = h_add(s1, cin)
    cout = '1' if (c1 == '1' or c2 == '1') else '0'
    return s2, cout

# Ripple-carry adder for two same-width bit-vectors
def add(bitsA: Bits, bitsB: Bits, cin: Bit = '0') -> Tuple[Bits, Bit]:
    assert len(bitsA) == len(bitsB)
    n = len(bitsA)
    out: Bits = ['0'] * n
    c = cin

    for i in range(n - 1, -1, -1):
        s, c = f_add(bitsA[i], bitsB[i], c)
        out[i] = s

    return out, c

# invert(bits): flips every bit ('0' -> '1', '1' -> '0')
def invert(bits: Bits) -> Bits:
    return ['1' if b == '0' else '0' for b in bits]

# negate(bits): two’s-complement negate = invert + 1
def negate(bits: Bits) -> Bits:
    inv = invert(bits)
    one = ['0'] * (len(bits) - 1) + ['1']
    s, _ = add(inv, one, '0')
    return s
