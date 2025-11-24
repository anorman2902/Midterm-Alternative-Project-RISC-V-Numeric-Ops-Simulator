# ------------------------------------------------------------
# Basic CPU integration test using prog.hex
# Ensures CPU loads a real program, executes instructions,
# and reaches a stable state without crashing.
# ------------------------------------------------------------

from pathlib import Path

from src.cpu_core.memory import Memory
from src.cpu_core.datapath import CPU
from src.cpu_core.prog_loader import load_prog_hex


# ------------------------------------------------------------
# Helper: resolve path to programs/*.hex
# ------------------------------------------------------------
def _hex_path(name: str) -> Path:
    return Path(__file__).parent / "programs" / name


# ------------------------------------------------------------
# Test 1 — program loads and runs without crashing
# ------------------------------------------------------------
def test_prog_runs_without_crashing():
    hex_file = _hex_path("prog.hex")
    assert hex_file.exists(), f"Missing prog.hex at {hex_file}"

    # Load program from file
    words = load_prog_hex(str(hex_file))

    # Create instruction + data memory
    imem = Memory(256)
    dmem = Memory(256)

    # Load instructions into instruction memory
    imem.load_program(words)

    # Construct CPU and run
    cpu = CPU(imem, dmem)

    # Run enough steps to execute all real instructions
    # (program ends in jal x0, 0 infinite loop)
    cpu.run(max_steps=50)

    assert True


# ------------------------------------------------------------
# Test 2 — verify expected final register state
# ------------------------------------------------------------
def test_prog_expected_registers():
    hex_file = _hex_path("prog.hex")
    words = load_prog_hex(str(hex_file))

    imem = Memory(256)
    dmem = Memory(256)
    imem.load_program(words)

    cpu = CPU(imem, dmem)
    cpu.run(max_steps=50)

    state = cpu.get_state()

    # prog.hex intended results:
    # x1 = 16
    # x2 = 42
    # x3 = lw from mem[x1] => 42
    # x4 = x3 + 1 => 43
    assert state.regs[1] == 16
    assert state.regs[2] == 42
    assert state.regs[3] == 42
    assert state.regs[4] == 43
