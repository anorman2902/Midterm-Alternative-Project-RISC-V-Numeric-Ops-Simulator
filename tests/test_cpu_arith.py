# tests/test_cpu_arith.py
import pytest
from src.cpu_core.datapath import SingleCycleCPU
from src.cpu_core.memory import Memory


# ------------------------------------------------------------
# Memory sizes for CPU tests
# ------------------------------------------------------------
IMEM_WORDS = 256
DMEM_WORDS = 256


# ------------------------------------------------------------
# Helper: Convert multi-line hex into a list of 32-bit words
# Each line = one instruction in hex.
# ------------------------------------------------------------
def load_hex_from_string(s: str):
    lines = [ln.strip() for ln in s.strip().splitlines() if ln.strip()]
    return [int(ln, 16) for ln in lines]


# ------------------------------------------------------------
# Helper: Load program into memory and execute until either:
#   - max_steps executed
#   - EBREAK (0x00100073) encountered
# This allows tests to embed instruction sequences directly.
# ------------------------------------------------------------
def run_hex_program(hex_text: str, max_steps: int = 200):
    # Create instruction + data memory
    imem = Memory(IMEM_WORDS)
    dmem = Memory(DMEM_WORDS)

    # Parse the inline hex program
    words = load_hex_from_string(hex_text)

    # Load words into instruction memory at sequential addresses
    for i, w in enumerate(words):
        imem.store_word(i * 4, w)

    # Instantiate the CPU
    cpu = SingleCycleCPU(imem, dmem)

    # Execute instructions
    for _ in range(max_steps):
        cpu.step()

        # Stop when EBREAK (0x00100073) is about to be fetched
        if imem.load_word(cpu.pc) == 0x00100073:
            cpu.step()  # Execute the EBREAK itself
            break

    return cpu, imem, dmem


# ------------------------------------------------------------
# Test 1: Basic ADD + SUB operations
# ------------------------------------------------------------
def test_add_sub_basic():
    hex_prog = """
    00500093      # addi x1, x0, 5
    00700113      # addi x2, x0, 7
    002081b3      # add  x3, x1, x2
    40110233      # sub  x4, x2, x1
    00100073      # ebreak
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 12   # 5 + 7 = 12
    assert rf.read(4) == 2    # 7 - 5 = 2


# ------------------------------------------------------------
# Test 2: AND / OR / XOR logic operations
# ------------------------------------------------------------
def test_logic_and_or_xor():
    hex_prog = """
    00f00093      # addi x1, x0, 15
    0f000113      # addi x2, x0, 240
    0020f1b3      # and x3, x1, x2   => 15 & 240  = 0
    0020e233      # or  x4, x1, x2   => 15 | 240  = 255
    0020c2b3      # xor x5, x1, x2   => 15 ^ 240  = 255
    00100073      # ebreak
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 0
    assert rf.read(4) == 255
    assert rf.read(5) == 255


# ------------------------------------------------------------
# Test 3: Shift instructions (SLL, SRL, SRA)
# ------------------------------------------------------------
def test_shifts_sll_srl_sra():
    hex_prog = """
    00100093      # addi x1, x0, 1
    00400113      # addi x2, x0, 4
    002091b3      # sll  x3, x1, x2   => 1 << 4  = 16
    0000d213      # srli x4, x1, 0    => 1 >> 0  = 1
    4010d293      # srai x5, x1, 1    => 1 >> 1  = 0 (arithmetic)
    00100073      # ebreak
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(3) == 16
    assert rf.read(4) == 1
    assert rf.read(5) == 0
