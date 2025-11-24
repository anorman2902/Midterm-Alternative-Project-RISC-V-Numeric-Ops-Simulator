# tests/test_cpu_branch_mem.py
import pytest
from src.cpu_core.memory import Memory
from src.cpu_core.datapath import SingleCycleCPU


# ------------------------------------------------------------
# Memory sizes for CPU tests
# ------------------------------------------------------------
IMEM_WORDS = 256
DMEM_WORDS = 256


# ------------------------------------------------------------
# Helper: Convert multi-line hex input to a list of 32-bit words.
# Used for embedding programs directly inside the test file.
# ------------------------------------------------------------
def load_hex_from_string(s: str):
    """
    Convert multi-line hex string into a list of 32-bit words.
    Allows inline comments (# or //), blank lines, optional 0x prefixes,
    and underscores for readability.
    """
    words = []
    for ln in s.strip().splitlines():
        ln = ln.strip()
        if not ln:
            continue

        # Strip comments
        ln = ln.split("#", 1)[0].split("//", 1)[0].strip()
        if not ln:
            continue

        # Allow underscores and 0x prefix
        ln = ln.replace("_", "")
        if ln.lower().startswith("0x"):
            ln = ln[2:]

        words.append(int(ln, 16) & 0xFFFF_FFFF)

    return words



# ------------------------------------------------------------
# Helper: Load embedded program into memory and execute until:
#   - max_steps reached, or
#   - EBREAK (0x00100073) is fetched.
# This mirrors the helper functions in the other test files.
# ------------------------------------------------------------
def run_hex_program(hex_text: str, max_steps: int = 200):
    # Create instruction + data memory
    imem = Memory(IMEM_WORDS)
    dmem = Memory(DMEM_WORDS)

    # Parse inline hex → list of instruction words
    words = load_hex_from_string(hex_text)

    # Load into imem sequentially (one word every 4 bytes)
    for i, w in enumerate(words):
        imem.store_word(i * 4, w)

    # Instantiate CPU
    cpu = SingleCycleCPU(imem, dmem)

    # Execute instructions
    for _ in range(max_steps):
        cpu.step()

        # Stop when we encounter EBREAK
        if imem.load_word(cpu.pc) == 0x00100073:
            cpu.step()     # Execute EBREAK
            break

    return cpu, imem, dmem


# ------------------------------------------------------------
# Test 1: STORE followed by LOAD
# Sequence:
#   - Write a value to memory
#   - Load it back
#   - Increment a register afterward
# ------------------------------------------------------------
def test_store_then_load_word():
    hex_prog = """
    01000093      # addi x1, x0, 16       (address)
    02a00113      # addi x2, x0, 42       (value)
    0020a023      # sw   x2, 0(x1)        (store 42 at addr 16)
    0000a183      # lw   x3, 0(x1)        (load it back into x3)
    00118213      # addi x4, x3, 1        (x4 = 42 + 1 = 43)
    00100073      # ebreak
    """

    cpu, _, dmem = run_hex_program(hex_prog)
    rf = cpu.regs

    # Register checks
    assert rf.read(1) == 16
    assert rf.read(2) == 42
    assert rf.read(3) == 42
    assert rf.read(4) == 43

    # Memory check
    assert dmem.load_word(16) == 42


# ------------------------------------------------------------
# Test 2: BLT-based loop that increments until x1 < x2 fails
# Program performs:
#
#   x1 = 0
#   x2 = 5
#   loop:
#       x1 = x1 + 1
#       if x1 < x2: branch back to loop
#
# After finishing, x1 == 5 and x2 == 5.
# ------------------------------------------------------------
def test_blt_loop_counts_to_five():
    hex_prog = """
    00000093      # addi x1, x0, 0
    00500113      # addi x2, x0, 5
    00108093      # addi x1, x1, 1
    fe20cee3      # blt  x1, x2, -4   (loop back)
    00100073      # ebreak
    """

    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.regs

    assert rf.read(2) == 5
    assert rf.read(1) == 5
