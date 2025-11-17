# src/cpu_core/run_cpu.py
import sys
from typing import Optional

from .prog_loader import load_prog_hex
from .memory import Memory
from .datapath import CPU


def run_program(
    hex_path: str,
    imem_words: int = 1024,
    dmem_words: int = 1024,
    max_steps: int = 10_000,
    pc_reset: int = 0,
) -> CPU:
    # Load program words from the hex file
    prog_words = load_prog_hex(hex_path)

    # Create instruction and data memories
    imem = Memory(imem_words)
    dmem = Memory(dmem_words)

    # Load program into instruction memory starting at address 0
    imem.load_program(prog_words, base_addr=0)

    # Create CPU and reset PC
    cpu = CPU(imem=imem, dmem=dmem, pc_reset=pc_reset)

    # Run for at most max_steps instructions
    cpu.run(max_steps=max_steps)

    return cpu


def _print_summary(cpu: CPU) -> None:
    state = cpu.get_state()
    print(f"Final PC  = 0x{state.pc:08X}")
    print("Registers:")
    for i, val in enumerate(state.regs):
        # Print registers in groups of 4 for readability
        label = f"x{i:02d}"
        print(f"  {label} = 0x{val:08X}")
    print(f"Total cycles: {cpu.cycle}")


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        print("Usage: python -m src.cpu_core.run_cpu path/to/prog.hex [max_steps]")
        return 1

    hex_path = argv[0]
    max_steps = 10_000

    if len(argv) >= 2:
        try:
            max_steps = int(argv[1])
        except ValueError:
            print(f"Invalid max_steps value: {argv[1]!r}")
            return 1

    cpu = run_program(hex_path, max_steps=max_steps)
    _print_summary(cpu)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
