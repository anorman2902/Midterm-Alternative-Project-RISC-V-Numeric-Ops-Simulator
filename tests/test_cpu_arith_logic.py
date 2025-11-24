# tests/test_cpu_arith_logic.py
import pytest
from src.cpu_core.memory import Memory
from src.cpu_core.datapath import SingleCycleCPU


# ------------------------------------------------------------
# Memory sizes used for all tests
# ------------------------------------------------------------
IMEM_WORDS = 256
DMEM_WORDS = 256


# ------------------------------------------------------------
# Helper: Convert multi-line hex string into a list of words
# Each line should contain exactly one 32-bit instruction in hex.
# ------------------------------------------------------------
def load_hex_from_string(s: str):
    lines = [ln.strip() for ln in s.strip().splitlines() if ln.strip()]
    return [int(ln, 16) for ln in lines]


# ------------------------------------------------------------
# Helper: Run a hex program directly from an inline string.
# This does NOT use a .hex file — it loads instructions into imem
# one word at a time, then steps the CPU until:
#   - max_steps is reached, OR
#   - an ECALL (0x00100073) is encountered
# ------------------------------------------------------------
def run_hex_program(hex_text: str, max_steps: int = 200):
    # Allocate instruction + data memory
    imem = Memory(IMEM_WORDS)
    dmem = Memory(DMEM_WORDS)

    # Parse hex into instruction words
    words = load_hex_from_string(hex_text)

    # Store instructions into imem, word-addressed
    for i, w in enumerate(words):
        imem.store_word(i * 4, w)

    # Create CPU instance
    cpu = SingleCycleCPU(imem, dmem)

    # Execute instructions
    for _ in range(max_steps):
        cpu.step()

        # Stop early if we hit ECALL (0x00100073)
        if imem.load_word(cpu.pc) == 0x00100073:
            cpu.step()   # Execute the ECALL itself
            break

    return cpu, imem, dmem


# ------------------------------------------------------------
# Test 1: Arithmetic + Logic + Shifts mix
# This sequence checks:
#   - addi
#   - add / sub
#   - and / or / xor
#   - sll / srl / sra
# ------------------------------------------------------------
def test_arith_logic_and_shifts():
    hex_prog = """
    00300093      # addi x1, x0, 3
    00400113      # addi x2, x0, 4
    002081b3      # add  x3, x1, x2
    40110233      # sub  x4, x2, x1
    0020f2b3      # and  x5, x1, x2
    0020e333      # or   x6, x1, x2
    0020c3b3      # xor  x7, x1, x2
    00209433      # sll  x8, x1, x2
    001154b3      # srl  x9, x2, x1
    40115533      # sra  x10, x2, x1
    00100073      # ecall (stop)
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    # Expected register values
    assert rf.read(1) == 3
    assert rf.read(2) == 4
    assert rf.read(3) == 7
    assert rf.read(4) == 1
    assert rf.read(5) == 0
    assert rf.read(6) == 7
    assert rf.read(7) == 7
    assert rf.read(8) == 48
    assert rf.read(9) == 0
    assert rf.read(10) == 0


# ------------------------------------------------------------
# Test 2: JAL changes PC and stores link in rd
# This validates jump + link behavior:
#   - JAL jumps over an instruction
#   - rd receives PC+4
# ------------------------------------------------------------
def test_jal_skips_instruction_and_sets_link():
    hex_prog = """
    00100093      # addi x1, x0, 1
    008002ef      # jal  x5, +8
    06300093      # addi x1, x0, 99   (should be skipped)
    00200113      # addi x2, x0, 2
    00100073      # ecall
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    # After JAL:
    assert rf.read(1) == 1     # overwritten instruction was skipped
    assert rf.read(2) == 2
    assert rf.read(5) == 8     # link register = PC+4
