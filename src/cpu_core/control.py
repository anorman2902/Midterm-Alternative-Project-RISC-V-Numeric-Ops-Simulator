from dataclasses import dataclass
from typing import Optional

from .isa import OPCODES, DecodedInstr

# ----------------------------------------
# ALU operation codes (simple string labels)
# ----------------------------------------
ALU_ADD   = "ADD"
ALU_SUB   = "SUB"
ALU_AND   = "AND"
ALU_OR    = "OR"
ALU_XOR   = "XOR"
ALU_SLT   = "SLT"
ALU_SLTU  = "SLTU"
ALU_SLL   = "SLL"
ALU_SRL   = "SRL"
ALU_SRA   = "SRA"
ALU_COPY_B = "COPY_B"   # used for LUI (load immediate into rd)

# ----------------------------------------
# Branch condition labels
# ----------------------------------------
BR_NONE = None
BR_EQ   = "EQ"
BR_NE   = "NE"
BR_LT   = "LT"
BR_GE   = "GE"
BR_LTU  = "LTU"
BR_GEU  = "GEU"

# ----------------------------------------
# Control signals structure (what the control unit outputs)
# ----------------------------------------
@dataclass
class ControlSignals:
    alu_op: str
    alu_src_imm: bool
    reg_write: bool
    mem_read: bool
    mem_write: bool
    mem_to_reg: bool
    branch_cond: Optional[str]
    jump: bool
    jalr: bool
    use_pc_plus_imm: bool
    use_imm_high: bool

# ============================================================
# AI-BEGIN
# This is the main "control unit" logic: given a decoded
# instruction, determine the correct control signals.
# It is long and full of cases because RV32I has many
# instruction formats, but the logic follows directly from
# the ISA specification.
# ============================================================
def decode_control(di: DecodedInstr) -> ControlSignals:
    """Generate all control signals for a decoded RV32I instruction."""

    opc = di.opcode
    f3 = di.funct3
    f7 = di.funct7

    # Default control: most things disabled.
    alu_op = ALU_ADD       # default ALU op
    alu_src_imm = False
    reg_write = False
    mem_read = False
    mem_write = False
    mem_to_reg = False
    branch_cond: Optional[str] = BR_NONE
    jump = False
    jalr = False
    use_pc_plus_imm = False
    use_imm_high = False

    # ---------------------------
    # R-type ALU operations
    # ---------------------------
    if opc == OPCODES["OP"]:
        reg_write = True
        alu_src_imm = False

        if f3 == 0b000 and f7 == 0b0000000:
            alu_op = ALU_ADD
        elif f3 == 0b000 and f7 == 0b0100000:
            alu_op = ALU_SUB
        elif f3 == 0b111:
            alu_op = ALU_AND
        elif f3 == 0b110:
            alu_op = ALU_OR
        elif f3 == 0b100:
            alu_op = ALU_XOR
        elif f3 == 0b010:
            alu_op = ALU_SLT
        elif f3 == 0b011:
            alu_op = ALU_SLTU
        elif f3 == 0b001:
            alu_op = ALU_SLL
        elif f3 == 0b101 and f7 == 0b0000000:
            alu_op = ALU_SRL
        elif f3 == 0b101 and f7 == 0b0100000:
            alu_op = ALU_SRA

    # ---------------------------
    # I-type ALU operations
    # ---------------------------
    elif opc == OPCODES["OP_IMM"]:
        reg_write = True
        alu_src_imm = True

        if f3 == 0b000:
            alu_op = ALU_ADD       # ADDI
        elif f3 == 0b111:
            alu_op = ALU_AND       # ANDI
        elif f3 == 0b110:
            alu_op = ALU_OR        # ORI
        elif f3 == 0b100:
            alu_op = ALU_XOR       # XORI
        elif f3 == 0b010:
            alu_op = ALU_SLT       # SLTI
        elif f3 == 0b011:
            alu_op = ALU_SLTU      # SLTIU
        elif f3 == 0b001:
            alu_op = ALU_SLL       # SLLI
        elif f3 == 0b101 and f7 == 0b0000000:
            alu_op = ALU_SRL       # SRLI
        elif f3 == 0b101 and f7 == 0b0100000:
            alu_op = ALU_SRA       # SRAI

    # ---------------------------
    # LOAD instructions
    # ---------------------------
    elif opc == OPCODES["LOAD"]:
        reg_write = True
        mem_read = True
        mem_to_reg = True      # write data from memory
        alu_src_imm = True     # address = rs1 + imm
        alu_op = ALU_ADD

    # ---------------------------
    # STORE instructions
    # ---------------------------
    elif opc == OPCODES["STORE"]:
        mem_write = True
        alu_src_imm = True
        alu_op = ALU_ADD      # address = rs1 + imm

    # ---------------------------
    # Branch instructions
    # ---------------------------
    elif opc == OPCODES["BRANCH"]:
        alu_op = ALU_SUB
        alu_src_imm = False
        reg_write = False

        if f3 == 0b000:
            branch_cond = BR_EQ
        elif f3 == 0b001:
            branch_cond = BR_NE
        elif f3 == 0b100:
            branch_cond = BR_LT
        elif f3 == 0b101:
            branch_cond = BR_GE
        elif f3 == 0b110:
            branch_cond = BR_LTU
        elif f3 == 0b111:
            branch_cond = BR_GEU

    # ---------------------------
    # Jump instructions (JAL, JALR)
    # ---------------------------
    elif opc == OPCODES["JAL"]:
        jump = True
        reg_write = True
        alu_op = ALU_ADD      # link address = PC + 4

    elif opc == OPCODES["JALR"]:
        jalr = True
        reg_write = True
        alu_src_imm = True
        alu_op = ALU_ADD

    # ---------------------------
    # Upper immediate instructions
    # ---------------------------
    elif opc == OPCODES["LUI"]:
        reg_write = True
        use_imm_high = True
        alu_op = ALU_COPY_B

    elif opc == OPCODES["AUIPC"]:
        reg_write = True
        use_pc_plus_imm = True
        alu_op = ALU_ADD
    # ============================================================
    # AI-END
    # ============================================================

    return ControlSignals(
        alu_op=alu_op,
        alu_src_imm=alu_src_imm,
        reg_write=reg_write,
        mem_read=mem_read,
        mem_write=mem_write,
        mem_to_reg=mem_to_reg,
        branch_cond=branch_cond,
        jump=jump,
        jalr=jalr,
        use_pc_plus_imm=use_pc_plus_imm,
        use_imm_high=use_imm_high,
    )
