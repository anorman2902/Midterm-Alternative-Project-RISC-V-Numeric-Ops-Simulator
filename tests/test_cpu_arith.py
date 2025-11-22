import pytest
from src.cpu_core.run_cpu import run_program
from src.cpu_core.memory import Memory
from src.cpu_core.regfile import RegFile
from src.cpu_core.cpu_single_cycle import SingleCycleCPU

# These helper functions generate tiny inline .hex programs.
def asm_to_hex(instrs):
    return "\n".join(f"{x:08x}" for x in instrs)


# --------------------------------------------------------------------
# Arithmetic and logical instruction tests
# --------------------------------------------------------------------

def test_add_sub_basic():
    instrs = [
        0x00500093,  # addi x1, x0, 5
        0x00700113,  # addi x2, x0, 7
        0x002081B3,  # add x3, x1, x2
        0x40110233,  # sub x4, x2, x1
        0x0000006F,  # jal x0, 0
    ]

    program = asm_to_hex(instrs)

    mem = Memory()
    mem.load_hex_from_string(program)
    regs = RegFile()

    cpu = SingleCycleCPU(mem, regs)
    run_program(cpu, max_steps=20)

    assert regs.read(3) == 12
    assert regs.read(4) == 2


def test_logic_and_or_xor():
    instrs = [
        0x00F00093,      # addi x1, x0, 15
        0x0F000113,      # addi x2, x0, 240
        0x0020F1B3,      # and x3, x1, x2   => 15 & 240 = 0
        0x0020E233,      # or  x4, x1, x2   => 15 | 240 = 255
        0x0020C2B3,      # xor x5, x1, x2   => 15 ^ 240 = 255
        0x0000006F,
    ]
    program = asm_to_hex(instrs)

    mem = Memory()
    mem.load_hex_from_string(program)
    regs = RegFile()
    cpu = SingleCycleCPU(mem, regs)
    run_program(cpu, max_steps=20)

    assert regs.read(3) == 0
    assert regs.read(4) == 255
    assert regs.read(5) == 255


def test_shifts_sll_srl_sra():
    instrs = [
        0x00100093,   # addi x1, x0, 1
        0x00400113,   # addi x2, x0, 4
        0x002091B3,   # sll x3, x1, x2   => 1 << 4 = 16
        0x0000D213,   # srli x4, x1, 0   => 1 >> 0 = 1
        0x4010D293,   # srai x5, x1, 1   => 1 >> 1 = 0
        0x0000006F,
    ]

    program = asm_to_hex(instrs)

    mem = Memory()
    mem.load_hex_from_string(program)
    regs = RegFile()
    cpu = SingleCycleCPU(mem, regs)
    run_program(cpu, max_steps=20)

    assert regs.read(3) == 16
    assert regs.read(4) == 1
    assert regs.read(5) == 0
