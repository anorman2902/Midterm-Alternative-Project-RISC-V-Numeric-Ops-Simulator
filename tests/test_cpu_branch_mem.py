import pytest
from src.cpu_core.memory import Memory
from src.cpu_core.datapath import SingleCycleCPU

IMEM_WORDS = 256
DMEM_WORDS = 256

def load_hex_from_string(s: str):
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
        if imem.load_word(cpu.pc) == 0x00100073:
            cpu.step()
            break

    return cpu, imem, dmem

def test_store_then_load_word():
    hex_prog = """
    01000093
    02a00113
    0020a023
    0000a183
    00118213
    00100073
    """
    cpu, _, dmem = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(1) == 16
    assert rf.read(2) == 42
    assert rf.read(3) == 42
    assert rf.read(4) == 43
    assert dmem.load_word(16) == 42


def test_blt_loop_counts_to_five():
    hex_prog = """
    00000093
    00500113
    00108093
    fe20cee3
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(2) == 5
    assert rf.read(1) == 5
