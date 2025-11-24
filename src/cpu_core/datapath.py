from dataclasses import dataclass
from typing import Optional

from .isa import (
    DecodedInstr,
    decode,
    OPCODES,
    imm_i,
    imm_s,
    imm_b,
    imm_u,
    imm_j,
)
from .regfile import RegFile
from .memory import Memory
from .control import (
    ControlSignals,
    decode_control,
    ALU_ADD,
    ALU_SUB,
    ALU_AND,
    ALU_OR,
    ALU_XOR,
    ALU_SLT,
    ALU_SLTU,
    ALU_SLL,
    ALU_SRL,
    ALU_SRA,
    ALU_COPY_B,
    BR_EQ,
    BR_NE,
    BR_LT,
    BR_GE,
    BR_LTU,
    BR_GEU,
)


# ----------------------------------------
# Basic CPU-wide constants
# ----------------------------------------
XLEN = 32
WORD_MASK = 0xFFFF_FFFF


# ----------------------------------------
# Simple helpers to enforce 32-bit arithmetic
# ----------------------------------------
def _mask32(x: int) -> int:
    return x & WORD_MASK


def _to_signed32(x: int) -> int:
    """Interpret x as a signed 32-bit integer."""
    x &= WORD_MASK
    if x & 0x8000_0000:
        return x - (1 << 32)
    return x


# ============================================================
# AI-BEGIN
# ALU logic: this is the main arithmetic/logic block.
# Even though each case is simple, handling shifts and signed
# comparisons requires care to match RV32I behavior.
# ============================================================
def _alu_execute(op: str, a: int, b: int) -> int:
    """Execute a single ALU operation using masked 32-bit values."""
    a32 = _mask32(a)
    b32 = _mask32(b)

    if op == ALU_ADD:
        res = a32 + b32
    elif op == ALU_SUB:
        res = a32 - b32
    elif op == ALU_AND:
        res = a32 & b32
    elif op == ALU_OR:
        res = a32 | b32
    elif op == ALU_XOR:
        res = a32 ^ b32
    elif op == ALU_SLL:
        res = a32 << (b32 & 0x1F)
    elif op == ALU_SRL:
        res = a32 >> (b32 & 0x1F)
    elif op == ALU_SRA:
        # Arithmetic shift requires a signed interpretation
        sa = _to_signed32(a32)
        res = sa >> (b32 & 0x1F)
    elif op == ALU_SLT:
        res = 1 if _to_signed32(a32) < _to_signed32(b32) else 0
    elif op == ALU_SLTU:
        res = 1 if a32 < b32 else 0
    elif op == ALU_COPY_B:
        res = b32
    else:
        res = 0  # fallback for unknown opcodes

    return _mask32(res)
# AI-END
# ============================================================


# ----------------------------------------
# Branch condition evaluation
# ----------------------------------------
def _branch_taken(cond: Optional[str], rs1_val: int, rs2_val: int) -> bool:
    if cond is None:
        return False

    a = _mask32(rs1_val)
    b = _mask32(rs2_val)
    sa = _to_signed32(a)
    sb = _to_signed32(b)

    if cond == BR_EQ:
        return a == b
    elif cond == BR_NE:
        return a != b
    elif cond == BR_LT:
        return sa < sb
    elif cond == BR_GE:
        return sa >= sb
    elif cond == BR_LTU:
        return a < b
    elif cond == BR_GEU:
        return a >= b
    return False


# ----------------------------------------
# CPU state snapshot
# ----------------------------------------
@dataclass
class CPUState:
    pc: int
    regs: list[int]


# ----------------------------------------
# Main single-cycle CPU implementation
# ----------------------------------------
class CPU:
    def __init__(self, imem: Memory, dmem: Memory, pc_reset: int = 0) -> None:
        self.imem = imem
        self.dmem = dmem
        self.regs = RegFile()
        self.pc = _mask32(pc_reset)
        self.cycle = 0  # number of executed instructions

    def reset(self, pc_reset: int = 0) -> None:
        """Reset PC and register file."""
        self.pc = _mask32(pc_reset)
        self.regs.reset()
        self.cycle = 0

    def get_state(self) -> CPUState:
        """Return the current PC and register snapshot."""
        return CPUState(pc=self.pc, regs=self.regs.dump())


    # ============================================================
    # AI-BEGIN
    # The core of the CPU: this executes exactly one instruction.
    # It implements fetch → decode → execute → memory → writeback
    # following the classic single-cycle datapath structure.
    # ============================================================
    def step(self) -> None:
        pc = self.pc
        pc_plus_4 = _mask32(pc + 4)

        # 1. Fetch
        instr_word = self.imem.load_word(pc)

        # 2. Decode instruction
        di: DecodedInstr = decode(instr_word)

        # 3. Generate control signals
        ctrl: ControlSignals = decode_control(di)

        # 4. Immediate generation (based on opcode type)
        opc = di.opcode
        imm = 0
        if opc in (OPCODES["OP_IMM"], OPCODES["LOAD"], OPCODES["JALR"]):
            imm = imm_i(instr_word)
        elif opc == OPCODES["STORE"]:
            imm = imm_s(instr_word)
        elif opc == OPCODES["BRANCH"]:
            imm = imm_b(instr_word)
        elif opc in (OPCODES["LUI"], OPCODES["AUIPC"]):
            imm = imm_u(instr_word)
        elif opc == OPCODES["JAL"]:
            imm = imm_j(instr_word)

        # 5. Register read
        rs1_val = self.regs.read(di.rs1)
        rs2_val = self.regs.read(di.rs2)

        # 6. Operand selection for ALU
        if ctrl.use_pc_plus_imm:
            op_a = pc
        else:
            op_a = rs1_val

        if ctrl.use_imm_high:
            op_b = imm             # LUI uses the upper immediate directly
        elif ctrl.alu_src_imm:
            op_b = imm             # I-type uses immediate
        else:
            op_b = rs2_val         # R-type uses register operand

        # 7. ALU execution
        alu_result = _alu_execute(ctrl.alu_op, op_a, op_b)

        # 8. Memory stage
        mem_data = 0
        if ctrl.mem_read:
            mem_data = self.dmem.load_word(alu_result)
        if ctrl.mem_write:
            self.dmem.store_word(alu_result, rs2_val)

        # 9. Write-back value selection
        wb_val = alu_result
        if ctrl.mem_to_reg:
            wb_val = mem_data
        if ctrl.jump or ctrl.jalr:
            wb_val = pc_plus_4  # link register = PC + 4

        # 10. Register write-back
        if ctrl.reg_write and di.rd != 0:
            self.regs.write(di.rd, wb_val)

        # 11. Next PC calculation
        next_pc = pc_plus_4

        # Branch
        if ctrl.branch_cond is not None:
            if _branch_taken(ctrl.branch_cond, rs1_val, rs2_val):
                next_pc = _mask32(pc + imm)

        # JAL
        if ctrl.jump:
            next_pc = _mask32(pc + imm)

        # JALR (must clear LSB)
        if ctrl.jalr:
            target = rs1_val + imm
            next_pc = _mask32(target & ~1)

        # 12. Commit next PC
        self.pc = next_pc
        self.cycle += 1
    # AI-END
    # ============================================================


    def run(self, max_steps: int = 10_000) -> None:
        """Run repeatedly for up to max_steps instructions."""
        for _ in range(max_steps):
            self.step()


# ----------------------------------------
# Compatibility alias for the tests
# ----------------------------------------
SingleCycleCPU = CPU
