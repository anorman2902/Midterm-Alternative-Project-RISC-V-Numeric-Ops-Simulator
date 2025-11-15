# src/numeric_core/shifter.py
from typing import List

# 0 or 1
Bit = str
Bits = List[Bit]

# left shift
def sll(bits: Bits, shamt: int) -> Bits:
    out = bits[:]
    for _ in range(shamt):
        out = out[1:] + ['0']
    return out

# right shift
def srl(bits: Bits, shamt: int) -> Bits:
    out = bits[:]
    for _ in range(shamt):
        out = ['0'] + out[:-1]
    return out

# arithmetic right shift
def sra(bits: Bits, shamt: int) -> Bits:
    out = bits[:]
    for _ in range(shamt):
        out = [out[0]] + out[:-1]
    return out
