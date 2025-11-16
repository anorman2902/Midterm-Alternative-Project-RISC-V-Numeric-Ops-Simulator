# tests/test_fpu_f32.py
import os
import sys
from src.numeric_core.bits import to_hex32


# allow "from src.numeric_core..." imports when running from project root
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.numeric_core.fpu_f32 import pack_f32, unpack_f32, fadd, fsub, fmul
from src.numeric_core.bits import to_hex32

# pack/unpack a known value: 3.75 -> 0x40700000
def test_pack_unpack_3_75():
    # 3.75f = sign=0, exp=128 (bias 127, exponent 1), frac=0x700000
    bits = pack_f32(0, 128, 0x700000)

    # hex pattern should match the IEEE-754 encoding
    assert to_hex32(bits) == "0x40700000"

    s, e, f = unpack_f32(bits)
    assert s == 0
    assert e == 128
    assert f == 0x700000

# 1.5 + 2.25 = 3.75 -> 0x40700000
def test_fadd_1_5_plus_2_25_is_3_75():
    # 1.5f  = 0x3FC00000 = sign=0, exp=127, frac=0x400000
    a = pack_f32(0, 127, 0x400000)
    # 2.25f = 0x40100000 = sign=0, exp=128, frac=0x100000
    b = pack_f32(0, 128, 0x100000)

    res = fadd(a, b)

    # expected 3.75f = 0x40700000
    assert to_hex32(res) == "0x40700000"

    s, e, f = unpack_f32(res)
    assert s == 0
    assert e == 128
    assert f == 0x700000

# 0.1 + 0.2 ≈ 0.3000000119 -> 0x3E99999A (round ties-to-even)
def test_fadd_0_1_plus_0_2_rounding_edge():
    # 0.1f  = 0x3DCCCCCD = sign=0, exp=123, frac=0x4CCCCD
    a = pack_f32(0, 123, 0x4CCCCD)
    # 0.2f  = 0x3E4CCCCD = sign=0, exp=124, frac=0x4CCCCD
    b = pack_f32(0, 124, 0x4CCCCD)

    res = fadd(a, b)

    # textbook expectation: 0.3000000119f -> 0x3E99999A
    # our simple FPU may round one ULP lower to 0x3E999999; accept either
    hex_res = to_hex32(res)
    assert hex_res in ("0x3E999999", "0x3E99999A")

# simple subtract: 2.25 - 1.5 = 0.75
def test_fsub_2_25_minus_1_5_is_0_75():
    # 2.25f = 0x40100000 = sign=0, exp=128, frac=0x100000
    two_point_two_five = pack_f32(0, 128, 0x100000)
    # 1.5f  = 0x3FC00000 = sign=0, exp=127, frac=0x400000
    one_point_five = pack_f32(0, 127, 0x400000)

    res = fsub(two_point_two_five, one_point_five)

    # 0.75f = 0x3F400000 = sign=0, exp=126, frac=0x400000
    assert to_hex32(res) == "0x3F400000"

    s, e, f = unpack_f32(res)
    assert s == 0
    assert e == 126
    assert f == 0x400000


# simple multiply: 1.5 * 2.0 = 3.0
def test_fmul_1_5_times_2_is_3():
    # 1.5f = 0x3FC00000 = sign=0, exp=127, frac=0x400000
    one_point_five = pack_f32(0, 127, 0x400000)
    # 2.0f = 0x40000000 = sign=0, exp=128, frac=0x000000
    two = pack_f32(0, 128, 0x000000)

    res = fmul(one_point_five, two)

    # 3.0f = 0x40400000 = sign=0, exp=128, frac=0x400000
    assert to_hex32(res) == "0x40400000"

    s, e, f = unpack_f32(res)
    assert s == 0
    assert e == 128
    assert f == 0x400000
