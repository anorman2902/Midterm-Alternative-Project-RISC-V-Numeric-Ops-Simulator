from dataclasses import dataclass

# ----------------------------------------
# RV32I base opcodes (simple constants)
# ----------------------------------------
OPCODES = {
    "OP":      0b0110011,  # R-type arithmetic (ADD, SUB, AND, OR, etc.)
    "OP_IMM":  0b0010011,  # I-type arithmetic (ADDI, ANDI, ORI, etc.)
    "LUI":     0b0110111,  # U-type: Load Upper Immediate
    "AUIPC":   0b0010111,  # U-type: Add Upper Immediate to PC
    "JAL":     0b1101111,  # J-type: Jump and Link
    "JALR":    0b1100111,  # I-type: Jump and Link Register
    "BRANCH":  0b1100011,  # B-type conditional branches
    "LOAD":    0b0000011,  # I-type loads
    "STORE":   0b0100011,  # S-type stores
}


# ----------------------------------------
# Basic field extractors (simple helpers)
# ----------------------------------------
def get_opcode(instr: int) -> int:
    """Return opcode from bits [6:0]."""
    return instr & 0x7F


def get_rd(instr: int) -> int:
    """Return rd from bits [11:7]."""
    return (instr >> 7) & 0x1F


def get_funct3(instr: int) -> int:
    """Return funct3 from bits [14:12]."""
    return (instr >> 12) & 0x7


def get_rs1(instr: int) -> int:
    """Return rs1 from bits [19:15]."""
    return (instr >> 15) & 0x1F


def get_rs2(instr: int) -> int:
    """Return rs2 from bits [24:20]."""
    return (instr >> 20) & 0x1F


def get_funct7(instr: int) -> int:
    """Return funct7 from bits [31:25]."""
    return (instr >> 25) & 0x7F



# ============================================================
# AI-BEGIN
# Sign extension helper used by all immediate builders.
# This must correctly interpret the top bit as the sign bit.
# ============================================================
def sign_extend(value: int, bits: int) -> int:
    """Sign-extend 'value' interpreted as a 'bits'-bit signed integer."""
    sign_bit = 1 << (bits - 1)
    mask = (1 << bits) - 1
    value &= mask
    return (value ^ sign_bit) - sign_bit
# AI-END
# ============================================================


# ----------------------------------------
# Immediate Types
# ----------------------------------------
def imm_i(instr: int) -> int:
    """Extract 12-bit I-type immediate, sign-extended."""
    raw = (instr >> 20) & 0xFFF
    return sign_extend(raw, 12)


def imm_s(instr: int) -> int:
    """Extract 12-bit S-type immediate, sign-extended."""
    imm_11_5 = (instr >> 25) & 0x7F
    imm_4_0  = (instr >> 7) & 0x1F
    raw = (imm_11_5 << 5) | imm_4_0
    return sign_extend(raw, 12)


# ============================================================
# AI-BEGIN
# B-type immediate decoding (branches).
# The bits are scattered and need to be reassembled carefully.
# ============================================================
def imm_b(instr: int) -> int:
    """Extract 13-bit B-type immediate (shifted by 1), sign-extended."""
    imm_12   = (instr >> 31) & 0x1
    imm_10_5 = (instr >> 25) & 0x3F
    imm_4_1  = (instr >> 8) & 0xF
    imm_11   = (instr >> 7) & 0x1

    raw = (
        (imm_12 << 12) |
        (imm_11 << 11) |
        (imm_10_5 << 5) |
        (imm_4_1 << 1)
    )
    return sign_extend(raw, 13)
# AI-END
# ============================================================


def imm_u(instr: int) -> int:
    """Extract upper 20 bits (already aligned to bit 12)."""
    return instr & 0xFFFFF000


# ============================================================
# AI-BEGIN
# J-type immediate decoding (JAL).
# Like B-type, JAL fields are split and must be recombined.
# ============================================================
def imm_j(instr: int) -> int:
    """Extract 21-bit J-type immediate (shifted by 1), sign-extended."""
    imm_20     = (instr >> 31) & 0x1
    imm_10_1   = (instr >> 21) & 0x3FF
    imm_11     = (instr >> 20) & 0x1
    imm_19_12  = (instr >> 12) & 0xFF

    raw = (
        (imm_20 << 20)     |
        (imm_19_12 << 12)  |
        (imm_11 << 11)     |
        (imm_10_1 << 1)
    )
    return sign_extend(raw, 21)
# AI-END
# ============================================================


# ----------------------------------------
# Decoded instruction container
# ----------------------------------------
@dataclass
class DecodedInstr:
    instr: int
    opcode: int
    rd: int
    rs1: int
    rs2: int
    funct3: int
    funct7: int


def decode(instr: int) -> DecodedInstr:
    """Decode top-level RV32I fields into a dataclass."""
    return DecodedInstr(
        instr=instr,
        opcode=get_opcode(instr),
        rd=get_rd(instr),
        rs1=get_rs1(instr),
        rs2=get_rs2(instr),
        funct3=get_funct3(instr),
        funct7=get_funct7(instr),
    )
