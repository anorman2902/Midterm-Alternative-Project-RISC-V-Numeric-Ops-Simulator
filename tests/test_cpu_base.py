# tests/test_cpu_base.py
from pathlib import Path

from src.cpu_core.run_cpu import run_program


# Path helper for the sample program.
# Adjust the path if you store test_base.hex somewhere else.
def _hex_path(name: str = "test_base.hex") -> Path:
    return Path(__file__).resolve().parent / "programs" / name


def test_base_runs_without_crashing():
    hex_file = _hex_path("test_base.hex")
    assert hex_file.exists(), f"Missing test program: {hex_file}"

    # Run with a limit on steps to avoid infinite loops.
    cpu = run_program(str(hex_file), max_steps=10_000)

    # Just basic sanity checks on state
    state = cpu.get_state()
    # PC should always be word-aligned (multiple of 4)
    assert state.pc % 4 == 0
    # There should be 32 registers
    assert len(state.regs) == 32


def test_base_expected_state():
    hex_file = _hex_path("test_base.hex")
    assert hex_file.exists(), f"Missing test program: {hex_file}"

    # You can tweak max_steps once you know roughly how many
    # instructions the sample program executes.
    cpu = run_program(str(hex_file), max_steps=10_000)
    state = cpu.get_state()

    # x0 must always remain 0
    assert state.regs[0] == 0

    # At least one other register should be non-zero if the program
    # actually sets up some values.
    non_zero_regs = [val for i, val in enumerate(state.regs) if i != 0 and val != 0]
    assert len(non_zero_regs) > 0, "Expected at least one non-zero register besides x0"

    # PC should not still be at reset after running
    assert state.pc != 0

    # PC always word-aligned
    assert state.pc % 4 == 0
