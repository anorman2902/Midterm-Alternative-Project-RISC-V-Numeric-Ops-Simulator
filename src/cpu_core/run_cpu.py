# src/cpu_core/run_cpu.py
import sys
from typing import Optional

from .prog_loader import load_prog_hex
from .memory import Memory
from .datapath import CPU


# ------------------------------------------------------------
# Program Runner Helper
# ------------------------------------------------------------
def run_program(
    hex_path: str,
    imem_words: int = 1024,
    dmem_words: int = 1024,
    max_steps: int = 10_000,
    pc_reset: int = 0,
) -> CPU:
    """
    Load a program from a .hex file into instruction memory,
    create a CPU, and run it for max_steps cycles.

    Returns the CPU instance so callers/tests can inspect state.
    """

    # Load program instructions as 32-bit words from the hex file
    prog_words = load_prog_hex(hex_path)

    # Create instruction memory (imem) and data memory (dmem)
    # Both are word-addressable and store 32-bit values.
    imem = Memory(imem_words)
    dmem = Memory(dmem_words)

    # Load program into instruction memory at address 0
    imem.load_program(prog_words, base_addr=0)

    # Create CPU and reset its program counter
    cpu = CPU(imem=imem, dmem=dmem, pc_reset=pc_reset)

    # Run the CPU for at most max_steps instructions
    cpu.run(max_steps=max_steps)

    return cpu


# ------------------------------------------------------------
# Pretty-print final CPU state for humans
# ------------------------------------------------------------
def _print_summary(cpu: CPU) -> None:
    """
    Display final PC, register contents, and cycle count.
    Used when running from the command line.
    """
    state = cpu.get_state()

    print(f"Final PC  = 0x{state.pc:08X}")
    print("Registers:")

    for i, val in enumerate(state.regs):
        # Print each register in hex (x00 ... x31)
        label = f"x{i:02d}"
        print(f"  {label} = 0x{val:08X}")

    print(f"Total cycles: {cpu.cycle}")


# ------------------------------------------------------------
# Command-line entry point
# ------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    """
    CLI usage:
      python -m src.cpu_core.run_cpu path/to/prog.hex [max_steps]
    """
    if argv is None:
        argv = sys.argv[1:]

    # Require at least the hex file path
    if len(argv) < 1:
        print("Usage: python -m src.cpu_core.run_cpu path/to/prog.hex [max_steps]")
        return 1

    hex_path = argv[0]

    # Default max_steps unless user overrides it
    max_steps = 10_000
    if len(argv) >= 2:
        try:
            max_steps = int(argv[1])
        except ValueError:
            print(f"Invalid max_steps value: {argv[1]!r}")
            return 1

    # Run program and print final CPU state
    cpu = run_program(hex_path, max_steps=max_steps)
    _print_summary(cpu)

    return 0


# ------------------------------------------------------------
# Allow running this file directly
# ------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(main())
