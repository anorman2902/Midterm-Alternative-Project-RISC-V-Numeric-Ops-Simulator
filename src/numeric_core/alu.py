# src/numeric_core/alu.py
from typing import Dict, List, Tuple
from .adders import add, negate

Bit = str       # '0' or '1'
Bits = List[Bit]

WIDTH = 32

# Compute NZCV flags for a 32-bit result
def flags_NZCV(result: Bits, carry_out: Bit, a_msb: Bit, b_msb: Bit) -> Dict[str,int]:
    N = 1 if result[0]=='1' else 0
    Z = 1 if all(b=='0' for b in result) else 0
    C = 1 if carry_out=='1' else 0
    # signed overflow for add
    r_msb = result[0]
    V = 1 if (a_msb == b_msb and r_msb != a_msb) else 0
    return {'N':N,'Z':Z,'C':C,'V':V}

# rs1 + rs2 (32-bit add)
def alu_add(rs1: Bits, rs2: Bits) -> Tuple[Bits, Dict[str,int]]:
    s, c = add(rs1, rs2, '0')
    f = flags_NZCV(s, c, rs1[0], rs2[0])
    return s, f

# rs1 - rs2 (implemented as rs1 + (-rs2))
def alu_sub(rs1: Bits, rs2: Bits) -> Tuple[Bits, Dict[str,int]]:
    nrs2 = negate(rs2)
    s, c = add(rs1, nrs2, '0')
    # use same overflow rule as add
    f = flags_NZCV(s, c, rs1[0], nrs2[0])
    return s, f