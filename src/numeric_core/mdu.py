# src/numeric_core/mdu.py
from typing import Dict, List, Tuple
from .adders import add, negate
from .shifter import sll
from .bits import zeros, ones, to_uint, zpad

Bit = str
Bits = List[Bit]

WIDTH = 32


# Convert bits (two's-complement) to signed int for tests / helpers.
def bits_to_signed(bits: Bits) -> int:
    u = to_uint(bits)
    if bits[0] == '1':
        return u - (1 << WIDTH)
    return u


# Convert Python int to WIDTH-bit two's-complement bits (for tests / helpers).
def int_to_bits(x: int) -> Bits:
    x &= (1 << WIDTH) - 1
    out: Bits = []
    for i in range(WIDTH - 1, -1, -1):
        out.append('1' if (x >> i) & 1 else '0')
    return out


# Unsigned compare: returns -1 if a<b, 0 if a==b, 1 if a>b.
def cmp_unsigned(a: Bits, b: Bits) -> int:
    assert len(a) == len(b)
    for i in range(len(a)):
        if a[i] != b[i]:
            return 1 if (a[i] == '1' and b[i] == '0') else -1
    return 0


# True if all bits are zero.
def is_zero(bits: Bits) -> bool:
    return all(b == '0' for b in bits)


# Unsigned restoring division on bit-vectors: dividend / divisor -> (q, r).
def unsigned_divmod_bits(dividend: Bits, divisor: Bits) -> Tuple[Bits, Bits]:
    n = len(dividend)
    R: Bits = ['0'] * n
    Q: Bits = ['0'] * n

    for i in range(n):
        # shift remainder left and bring in next dividend bit
        R = sll(R, 1)
        R[-1] = dividend[i]

        # shift quotient left to make room for next bit
        Q = sll(Q, 1)

        # if R >= divisor, subtract and set quotient bit
        if cmp_unsigned(R, divisor) >= 0:
            R, _ = add(R, negate(divisor))
            Q[-1] = '1'

    return Q, R


# Unsigned multiply: returns (hi, lo) 64-bit product split into two 32-bit vectors.
def mul_unsigned(rs1: Bits, rs2: Bits) -> Tuple[Bits, Bits]:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    acc: Bits = ['0'] * (2 * WIDTH)          # 64-bit accumulator
    m = zpad(rs1, 2 * WIDTH)                 # zero-extend multiplicand to 64 bits
    n = WIDTH

    for i in range(n):
        # check bit i from the right (LSB-first in rs2)
        if rs2[n - 1 - i] == '1':
            # shift multiplicand left by i and add into accumulator
            shifted = m[:]
            for _ in range(i):
                shifted = sll(shifted, 1)
            acc, _ = add(acc, shifted)

    hi = acc[:WIDTH]
    lo = acc[WIDTH:]
    return hi, lo


# Signed multiply: multiplies two two's-complement operands, returns (hi, lo).
def mul_signed(rs1: Bits, rs2: Bits) -> Tuple[Bits, Bits]:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    sign_a = rs1[0]
    sign_b = rs2[0]

    # magnitudes (absolute values)
    mag_a = rs1[:] if sign_a == '0' else negate(rs1)
    mag_b = rs2[:] if sign_b == '0' else negate(rs2)

    hi_u, lo_u = mul_unsigned(mag_a, mag_b)
    res64: Bits = hi_u + lo_u

    # if signs are the same, result is non-negative
    if sign_a == sign_b:
        return res64[:WIDTH], res64[WIDTH:]

    # otherwise negate full 64-bit product
    neg64 = negate(res64)
    return neg64[:WIDTH], neg64[WIDTH:]


# RV32M DIVU: unsigned divide, quotient only.
def div_unsigned(rs1: Bits, rs2: Bits) -> Bits:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    # x / 0 -> q = 0xFFFFFFFF
    if is_zero(rs2):
        return ones(WIDTH)

    q, _ = unsigned_divmod_bits(rs1, rs2)
    return q


# RV32M REMU: unsigned remainder.
def rem_unsigned(rs1: Bits, rs2: Bits) -> Bits:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    # x / 0 -> r = dividend
    if is_zero(rs2):
        return rs1[:]

    _, r = unsigned_divmod_bits(rs1, rs2)
    return r


# 32-bit patterns for INT_MIN and -1 in two's-complement.
INT_MIN_BITS: Bits = ['1'] + ['0'] * (WIDTH - 1)
NEG_ONE_BITS: Bits = ['1'] * WIDTH


# RV32M DIV: signed divide (truncates toward zero).
def div_signed(rs1: Bits, rs2: Bits) -> Bits:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    # divide-by-zero: quotient = -1
    if is_zero(rs2):
        return NEG_ONE_BITS[:]

    # INT_MIN / -1 -> INT_MIN (overflow case)
    if rs1 == INT_MIN_BITS and rs2 == NEG_ONE_BITS:
        return INT_MIN_BITS[:]

    sign_a = rs1[0]
    sign_b = rs2[0]

    mag_a = rs1[:] if sign_a == '0' else negate(rs1)
    mag_b = rs2[:] if sign_b == '0' else negate(rs2)

    q_mag, _ = unsigned_divmod_bits(mag_a, mag_b)

    # sign(q) = sign(a) XOR sign(b)
    same_sign = (sign_a == sign_b)
    q = q_mag[:] if same_sign else negate(q_mag)

    return q


# RV32M REM: signed remainder (same sign as dividend).
def rem_signed(rs1: Bits, rs2: Bits) -> Bits:
    assert len(rs1) == WIDTH and len(rs2) == WIDTH

    # divide-by-zero: remainder = dividend
    if is_zero(rs2):
        return rs1[:]

    # INT_MIN / -1 -> remainder = 0
    if rs1 == INT_MIN_BITS and rs2 == NEG_ONE_BITS:
        return ['0'] * WIDTH

    sign_a = rs1[0]
    sign_b = rs2[0]

    mag_a = rs1[:] if sign_a == '0' else negate(rs1)
    mag_b = rs2[:] if sign_b == '0' else negate(rs2)

    q_mag, r_mag = unsigned_divmod_bits(mag_a, mag_b)

    # remainder sign = sign of dividend
    r = r_mag[:] if sign_a == '0' else negate(r_mag)

    return r


# Simple helper used earlier in the project: low 32 bits of signed multiply.
def mul_low(rs1: Bits, rs2: Bits) -> Dict[str, object]:
    hi, lo = mul_signed(rs1, rs2)
    return {
        'rd_bits': lo,
        'overflow': 0,
        'trace': [],  # detailed trace not needed for core tests
    }
