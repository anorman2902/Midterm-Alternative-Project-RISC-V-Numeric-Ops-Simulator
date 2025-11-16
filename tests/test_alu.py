# tests/test_alu_add_sub.py
import os
import sys

# allow "from src.numeric_core..." imports when running from project root
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.numeric_core.bits import from_uint, to_hex32
from src.numeric_core.alu import alu_add, alu_sub
from src.numeric_core.twos import decode_twos_complement


# 0x7FFFFFFF + 0x00000001 → 0x80000000; V=1, C=0, N=1, Z=0
def test_alu_add_pos_overflow():
    rs1 = from_uint(0x7FFFFFFF, 32)
    rs2 = from_uint(0x00000001, 32)

    result, flags = alu_add(rs1, rs2)

    assert to_hex32(result) == "0x80000000"
    assert flags["V"] == 1
    assert flags["C"] == 0
    assert flags["N"] == 1
    assert flags["Z"] == 0


# 0x80000000 - 0x00000001 → 0x7FFFFFFF; V=1, C=1, N=0, Z=0
def test_alu_sub_neg_overflow():
    rs1 = from_uint(0x80000000, 32)
    rs2 = from_uint(0x00000001, 32)

    result, flags = alu_sub(rs1, rs2)

    assert to_hex32(result) == "0x7FFFFFFF"
    assert flags["V"] == 1
    assert flags["C"] == 1
    assert flags["N"] == 0
    assert flags["Z"] == 0


# -1 + -1 → -2; V=0, C=1, N=1, Z=0
def test_alu_add_minus_one_plus_minus_one():
    # -1 = 0xFFFFFFFF, -2 = 0xFFFFFFFE
    rs1 = from_uint(0xFFFFFFFF, 32)
    rs2 = from_uint(0xFFFFFFFF, 32)

    result, flags = alu_add(rs1, rs2)

    assert to_hex32(result) == "0xFFFFFFFE"
    dec = decode_twos_complement(result)["value"]
    assert dec == -2

    assert flags["V"] == 0
    assert flags["C"] == 1
    assert flags["N"] == 1
    assert flags["Z"] == 0


# 13 + -13 → 0; V=0, C=1, N=0, Z=1
def test_alu_add_thirteen_plus_minus_thirteen():
    # 13 = 0x0000000D, -13 = 0xFFFFFFF3
    rs1 = from_uint(0x0000000D, 32)
    rs2 = from_uint(0xFFFFFFF3, 32)

    result, flags = alu_add(rs1, rs2)

    assert to_hex32(result) == "0x00000000"
    dec = decode_twos_complement(result)["value"]
    assert dec == 0

    assert flags["V"] == 0
    assert flags["C"] == 1
    assert flags["N"] == 0
    assert flags["Z"] == 1
