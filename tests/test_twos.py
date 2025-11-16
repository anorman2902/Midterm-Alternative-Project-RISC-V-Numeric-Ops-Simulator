# tests/test_twos.py
import os
import sys

# allow "from src.numeric_core..." imports when running from project root
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.numeric_core.twos import (
    encode_twos_complement,
    decode_twos_complement,
    sign_extend,
    zero_extend,
)

# check hex patterns for common sample values
def test_encode_twos_samples_hex():
    cases = [
        (-2**31, "0x80000000"),  # INT_MIN
        (-1,      "0xFFFFFFFF"),
        (-13,     "0xFFFFFFF3"),
        (-7,      "0xFFFFFFF9"),
        (0,       "0x00000000"),
        (13,      "0x0000000D"),
        (2**31-1, "0x7FFFFFFF"),  # INT_MAX
    ]

    for val, expected_hex in cases:
        enc = encode_twos_complement(val)
        assert enc["hex"] == expected_hex
        assert enc["overflow_flag"] == 0

# values that do fit should round-trip encode -> decode
def test_encode_decode_roundtrip_in_range():
    values = [
        -2**31,
        -1,
        -13,
        -7,
        0,
        13,
        2**31 - 1,
    ]

    for v in values:
        enc = encode_twos_complement(v)
        dec = decode_twos_complement(enc["bits"])
        assert dec["value"] == v
        assert enc["overflow_flag"] == 0

# out-of-range value should set overflow_flag
def test_overflow_flag_for_out_of_range_value():
    # just past INT_MAX
    enc = encode_twos_complement(2**31)
    assert enc["overflow_flag"] == 1

    # way below INT_MIN
    enc2 = encode_twos_complement(-(2**31) - 1)
    assert enc2["overflow_flag"] == 1

# sign_extend should copy the sign bit
def test_sign_extend_negative_and_positive():
    # 4-bit -1: 1111
    bits_neg = ['1', '1', '1', '1']
    se_neg = sign_extend(bits_neg, 8)
    assert se_neg == ['1', '1', '1', '1'] + bits_neg

    # 4-bit +3: 0011
    bits_pos = ['0', '0', '1', '1']
    se_pos = sign_extend(bits_pos, 8)
    # top bits should be copies of original sign (0)
    assert se_pos == ['0', '0', '0', '0'] + bits_pos

# zero_extend should always add zeros on the left
def test_zero_extend():
    # 4-bit pattern 1010
    bits = ['1', '0', '1', '0']
    ze = zero_extend(bits, 8)
    assert ze == ['0', '0', '0', '0'] + bits
