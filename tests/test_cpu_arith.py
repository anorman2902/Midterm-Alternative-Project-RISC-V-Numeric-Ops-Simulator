import pytest
from src.cpu_core.datapath import SingleCycleCPU
from src.cpu_core.memory import Memory

IMEM_WORDS = 256
DMEM_WORDS = 256

def load_hex_from_string(s: str):
    """Parse one 32-bit hex instruction per line."""
    lines = [ln.strip() for ln in s.strip().splitlines() if ln.strip()]
    return [int(ln, 16) for ln in lines]

def run_hex_program(hex_text: str, max_steps: int = 200):
    imem = Memory(IMEM_WORDS)
    dmem = Memory(DMEM_WORDS)

    words = load_hex_from_string(hex_text)
    for i, w in enumerate(words):
        imem.store_word(i * 4, w)

    cpu = SingleCycleCPU(imem, dmem)

    for _ in range(max_steps):
        cpu.step()
        # stop after executing EBREAK (0x00100073)
        if imem.load_word(cpu.pc) == 0x00100073:
            cpu.step()
            break

    return cpu, imem, dmem


def test_add_sub_basic():
    hex_prog = """
    00500093
    00700113
    002081b3
    40110233
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 12
    assert rf.read(4) == 2


def test_logic_and_or_xor():
    hex_prog = """
    00f00093
    0f000113
    0020f1b3
    0020e233
    0020c2b3
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 0
    assert rf.read(4) == 255
    assert rf.read(5) == 255


def test_shifts_sll_srl_sra():
    hex_prog = """
    00100093
    00400113
    002091b3
    0000d213
    4010d293
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 16
    assert rf.read(4) == 1
    assert rf.read(5) == 0
