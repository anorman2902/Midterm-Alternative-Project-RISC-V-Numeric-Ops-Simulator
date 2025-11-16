# tests/test_bits.py
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.numeric_core.bits import (
    Bit,
    Bits,
    zpad,
    ones,
    zeros,
    from_uint,
    to_uint,
    pretty_bin32,
    to_hex32,
)

def test_zpad_basic():
    b = ['1', '0', '1']
    out = zpad(b, 5)
    assert out == ['0', '0', '1', '0', '1']

def test_ones_zeros():
    assert ones(4) == ['1', '1', '1', '1']
    assert zeros(3) == ['0', '0', '0']

def test_from_uint_and_to_uint_roundtrip():
    n = 13
    bits = from_uint(n, 32)
    assert len(bits) == 32
    assert to_uint(bits) == n

def test_to_hex32_and_pretty_bin32():
    n = 0x0000000D
    bits = from_uint(n, 32)
    assert to_hex32(bits) == "0x0000000D"

    pretty = pretty_bin32(bits)
    # should be 4 groups of 8 bits
    parts = pretty.split("_")
    assert len(parts) == 4
    assert "".join(parts) == "".join(bits)
