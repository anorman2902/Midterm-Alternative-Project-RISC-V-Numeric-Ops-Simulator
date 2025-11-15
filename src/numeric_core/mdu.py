# src/numeric_core/mdu.py
from typing import Dict, List, Tuple
from .bits import Bits, to_uint
from .adders import add, negate
from .shifter import sll, sra

WIDTH = 32

# convert signed 32-bit bit-vector to Python int
def bits_to_signed(bits: Bits) -> int:
    if bits[0] == '0':
        return to_uint(bits)
    neg = negate(bits)
    return -to_uint(neg)

# multiply two signed numbers (shift-and-add)
def mul_signed(rs1: Bits, rs2: Bits) -> Tuple[Bits, Bits]:
    a = bits_to_signed(rs1)
    b = bits_to_signed(rs2)
    prod = a * b
    # 64-bit result split into hi and lo
    lo = prod & 0xFFFFFFFF
    hi = (prod >> 32) & 0xFFFFFFFF
    return int_to_bits(hi), int_to_bits(lo)

# multiply two unsigned numbers
def mul_unsigned(rs1: Bits, rs2: Bits) -> Tuple[Bits, Bits]:
    a = to_uint(rs1)
    b = to_uint(rs2)
    prod = a * b
    lo = prod & 0xFFFFFFFF
    hi = (prod >> 32) & 0xFFFFFFFF
    return int_to_bits(hi), int_to_bits(lo)

# signed division (RV32M behavior)
def div_signed(rs1: Bits, rs2: Bits) -> Bits:
    a = bits_to_signed(rs1)
    b = bits_to_signed(rs2)
    if b == 0:
        return int_to_bits(-1)     # division by zero = -1
    if a == -2**31 and b == -1:
        return int_to_bits(a)      # overflow case = dividend
    return int_to_bits(a // b)

# unsigned division
def div_unsigned(rs1: Bits, rs2: Bits) -> Bits:
    a = to_uint(rs1)
    b = to_uint(rs2)
    if b == 0:
        return int_to_bits(0xFFFFFFFF)
    return int_to_bits(a // b)

# signed remainder (RV32M behavior)
def rem_signed(rs1: Bits, rs2: Bits) -> Bits:
    a = bits_to_signed(rs1)
    b = bits_to_signed(rs2)
    if b == 0:
        return int_to_bits(a)
    if a == -2**31 and b == -1:
        return int_to_bits(0)
    return int_to_bits(a % b)

# unsigned remainder
def rem_unsigned(rs1: Bits, rs2: Bits) -> Bits:
    a = to_uint(rs1)
    b = to_uint(rs2)
    if b == 0:
        return int_to_bits(a)
    return int_to_bits(a % b)


# helper: convert Python int → 32-bit two's complement bit-vector
def int_to_bits(x: int) -> Bits:
    x &= 0xFFFFFFFF
    out: Bits = []
    for i in range(WIDTH-1, -1, -1):
        out.append('1' if (x >> i) & 1 else '0')
    return out
