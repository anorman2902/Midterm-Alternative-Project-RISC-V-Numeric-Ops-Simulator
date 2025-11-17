# src/cpu_core/control.py
from dataclasses import dataclass
from typing import Optional

from .isa import OPCODES, DecodedInstr

ALU_ADD = "ADD"
ALU_SUB = "SUB"
ALU_AND = "AND"
ALU_OR  = "OR"
ALU_XOR = "XOR"
ALU_SLT = "SLT"
ALU_SLTU = "SLTU"
ALU_SLL = "SLL"
ALU_SRL = "SRL"
ALU_SRA = "SRA"
ALU_COPY_B = "COPY_B"  # used for LUI (load immediate into rd)

BR_NONE = None
BR_EQ   = "EQ"
BR_NE   = "NE"
BR_LT   = "LT"
BR_GE   = "GE"
BR_LTU  = "LTU"
BR_GEU  = "GEU"

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


def decode_control(di: DecodedInstr) -> ControlSignals:
    opc = di.opcode
    f3 = di.funct3
    f7 = di.funct7

    # Default: no memory access, no branch, no jump.
    # ALU defaults to ADD, with rs2 as second operand.
    alu_op = ALU_ADD
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

    if opc == OPCODES["OP"]:
        reg_write = True
        alu_src_imm = False

        if f3 == 0b000 and f7 == 0b0000000:
            alu_op = ALU_ADD          # ADD
        elif f3 == 0b000 and f7 == 0b0100000:
            alu_op = ALU_SUB          # SUB
        elif f3 == 0b111:
            alu_op = ALU_AND          # AND
        elif f3 == 0b110:
            alu_op = ALU_OR           # OR
        elif f3 == 0b100:
            alu_op = ALU_XOR          # XOR
        elif f3 == 0b010:
            alu_op = ALU_SLT          # SLT (signed)
        elif f3 == 0b011:
            alu_op = ALU_SLTU         # SLTU (unsigned)
        elif f3 == 0b001:
            alu_op = ALU_SLL          # SLL
        elif f3 == 0b101 and f7 == 0b0000000:
            alu_op = ALU_SRL          # SRL
        elif f3 == 0b101 and f7 == 0b0100000:
            alu_op = ALU_SRA          # SRA

    elif opc == OPCODES["OP_IMM"]:
        reg_write = True
        alu_src_imm = True

        if f3 == 0b000:
            alu_op = ALU_ADD          # ADDI
        elif f3 == 0b111:
            alu_op = ALU_AND          # ANDI
        elif f3 == 0b110:
            alu_op = ALU_OR           # ORI
        elif f3 == 0b100:
            alu_op = ALU_XOR          # XORI
        elif f3 == 0b010:
            alu_op = ALU_SLT          # SLTI
        elif f3 == 0b011:
            alu_op = ALU_SLTU         # SLTIU
        elif f3 == 0b001:
            alu_op = ALU_SLL          # SLLI
        elif f3 == 0b101 and f7 == 0b0000000:
            alu_op = ALU_SRL          # SRLI
        elif f3 == 0b101 and f7 == 0b0100000:
            alu_op = ALU_SRA          # SRAI

    elif opc == OPCODES["LOAD"]:
        reg_write = True
        mem_read = True
        mem_to_reg = True      # write-back comes from memory
        alu_src_imm = True     # base + offset
        alu_op = ALU_ADD       # address = rs1 + imm

    elif opc == OPCODES["STORE"]:
        mem_write = True
        alu_src_imm = True     # base + offset
        alu_op = ALU_ADD       # address = rs1 + imm

    elif opc == OPCODES["BRANCH"]:
        alu_op = ALU_SUB       # often used for comparisons
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

    elif opc == OPCODES["JAL"]:
        jump = True
        reg_write = True
        alu_op = ALU_ADD       # for PC + 4 (link address)
        # ALU inputs for PC+4 will be chosen in the datapath

    elif opc == OPCODES["JALR"]:
        jalr = True
        reg_write = True
        alu_src_imm = True     # base register + offset
        alu_op = ALU_ADD

    elif opc == OPCODES["LUI"]:
        reg_write = True
        use_imm_high = True
        alu_op = ALU_COPY_B    # treat imm as the "B" operand

    elif opc == OPCODES["AUIPC"]:
        reg_write = True
        use_pc_plus_imm = True
        alu_op = ALU_ADD

    # For any unrecognized opcode, the defaults remain:
    # no writes, no memory access, no branch, no jump.

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
