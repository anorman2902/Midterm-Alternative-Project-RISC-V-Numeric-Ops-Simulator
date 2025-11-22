"""
RV32I CPU integration tests: arithmetic, logic, shifts, and JAL control flow.

These tests load tiny hex programs into instruction memory, run the CPU
for a bounded number of steps, and check final register values.

If your loader/CPU class names differ slightly, adjust ONLY the helper
section at the top.
"""

import pytest

try:
    # Most likely layout from our cpu_core commits
    from src.cpu_core.memory import Memory
    from src.cpu_core.cpu_single_cycle import SingleCycleCPU
    from src.cpu_core.prog_loader import load_hex_from_string
except Exception:
    # Fallback: if you named things slightly differently
    from src.cpu_core.memory import Memory
    from src.cpu_core.datapath import SingleCycleCPU

    def load_hex_from_string(s: str):
        lines = [ln.strip() for ln in s.strip().splitlines() if ln.strip()]
        return [int(ln, 16) for ln in lines]


def run_hex_program(hex_text: str, max_steps: int = 200):
    imem = Memory()
    dmem = Memory()

    words = load_hex_from_string(hex_text)

    # Our Memory class supported word writes via store_word(addr, value)
    # and treated addresses as byte addresses.
    for i, w in enumerate(words):
        imem.store_word(i * 4, w)

    cpu = SingleCycleCPU(imem=imem, dmem=dmem)

    for _ in range(max_steps):
        cpu.step()
        # We used EBREAK (0x00100073) as a stop sentinel.
        if getattr(cpu, "halted", False):
            break

    return cpu, imem, dmem


def test_arith_logic_and_shifts():
    hex_prog = """
    00300093
    00400113
    002081b3
    40110233
    0020f2b3
    0020e333
    0020c3b3
    00209433
    001154b3
    40115533
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)

    rf = cpu.rf  # register file from our earlier commits

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


def test_jal_skips_instruction_and_sets_link():
    hex_prog = """
    00100093
    008002ef
    06300093
    00200113
    00100073
    """
    cpu, _, _ = run_hex_program(hex_prog)
    rf = cpu.rf

    assert rf.read(1) == 1
    assert rf.read(2) == 2
    assert rf.read(5) == 8
