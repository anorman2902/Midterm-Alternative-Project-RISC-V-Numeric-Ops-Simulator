# tests/test_mdu.py
import os
import sys

# allow "from src.numeric_core..." imports when running from project root
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.numeric_core.bits import from_uint, to_uint, to_hex32
from src.numeric_core.mdu import (
    bits_to_signed,
    mul_signed,
    mul_unsigned,
    div_signed,
    div_unsigned,
    rem_signed,
    rem_unsigned,
)

INT_MIN = 0x80000000

# basic unsigned multiply: low 32 bits and hex
def test_mul_unsigned_small():
    a = from_uint(6, 32)
    b = from_uint(7, 32)

    hi, lo = mul_unsigned(a, b)

    assert to_uint(hi) == 0
    assert to_uint(lo) == 42
    assert to_hex32(lo) == "0x0000002A"

# MUL 12345678 * -87654321 → low 32 bits 0xD91D0712 (example from spec)
def test_mul_signed_large_example_low32():
    a = from_uint(12345678, 32)
    # -87654321 in two's complement
    b = from_uint(0xFAC6804F, 32)

    hi, lo = mul_signed(a, b)

    assert to_hex32(lo) == "0xD91D0712"


# DIV -7 / 3 → q = -2 (0xFFFFFFFE); r = -1 (0xFFFFFFFF)
def test_div_signed_minus7_over_3():
    rs1 = from_uint(0xFFFFFFF9, 32)  # -7
    rs2 = from_uint(3, 32)

    q_bits = div_signed(rs1, rs2)
    r_bits = rem_signed(rs1, rs2)

    assert bits_to_signed(q_bits) == -2
    assert bits_to_signed(r_bits) == -1

    assert to_hex32(q_bits) == "0xFFFFFFFE"
    assert to_hex32(r_bits) == "0xFFFFFFFF"

# DIVU 0x80000000 / 3 → q = 0x2AAAAAAA; r = 0x00000002
def test_div_unsigned_example_from_spec():
    rs1 = from_uint(0x80000000, 32)
    rs2 = from_uint(3, 32)

    q_bits = div_unsigned(rs1, rs2)
    r_bits = rem_unsigned(rs1, rs2)

    assert to_hex32(q_bits) == "0x2AAAAAAA"
    assert to_hex32(r_bits) == "0x00000002"

# DIV x / 0 semantics (signed): q = -1, r = dividend
def test_div_signed_divide_by_zero():
    rs1 = from_uint(0x0000002A, 32)  # 42
    rs2 = from_uint(0x00000000, 32)  # 0

    q_bits = div_signed(rs1, rs2)
    r_bits = rem_signed(rs1, rs2)

    assert bits_to_signed(q_bits) == -1
    assert bits_to_signed(r_bits) == 42

    assert to_hex32(q_bits) == "0xFFFFFFFF"
    assert to_hex32(r_bits) == "0x0000002A"

# DIVU x / 0 semantics (unsigned): q = 0xFFFFFFFF, r = dividend
def test_div_unsigned_divide_by_zero():
    rs1 = from_uint(0x0000002A, 32)  # 42
    rs2 = from_uint(0x00000000, 32)

    q_bits = div_unsigned(rs1, rs2)
    r_bits = rem_unsigned(rs1, rs2)

    assert to_uint(q_bits) == 0xFFFFFFFF
    assert to_uint(r_bits) == 0x0000002A

    assert to_hex32(q_bits) == "0xFFFFFFFF"
    assert to_hex32(r_bits) == "0x0000002A"

# DIV INT_MIN / -1 → q = INT_MIN (0x80000000), r = 0
def test_div_signed_int_min_over_minus_one():
    rs1 = from_uint(INT_MIN, 32)        # INT_MIN
    rs2 = from_uint(0xFFFFFFFF, 32)     # -1

    q_bits = div_signed(rs1, rs2)
    r_bits = rem_signed(rs1, rs2)

    assert to_hex32(q_bits) == "0x80000000"
    assert to_hex32(r_bits) == "0x00000000"

    assert bits_to_signed(q_bits) == -2**31
    assert bits_to_signed(r_bits) == 0
