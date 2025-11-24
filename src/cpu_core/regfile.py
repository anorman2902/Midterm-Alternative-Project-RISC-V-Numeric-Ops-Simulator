# src/cpu_core/regfile.py
from typing import List

# ------------------------------------------------------------
# Register File Constants
# ------------------------------------------------------------
NUM_REGS = 32   # RV32I has 32 integer registers: x0–x31
XLEN = 32       # Architecture width in bits


# ------------------------------------------------------------
# Basic helpers (simple ↠ no AI tag needed)
# ------------------------------------------------------------
def _check_idx(idx: int) -> None:
    """Ensure a register index is in the valid range 0–31."""
    if not (0 <= idx < NUM_REGS):
        raise IndexError(f"Register index out of range: {idx}")


def _mask32(value: int) -> int:
    """Force a Python int to behave like a 32-bit hardware register."""
    return value & 0xFFFF_FFFF


# ------------------------------------------------------------
# Register File (x0 hard-wired to zero)
# ------------------------------------------------------------
class RegFile:
    """
    A simple RV32I 32-register file.

    • x0 is permanently zero (writes to x0 are ignored)
    • All other registers store 32-bit values
    • Internally, we use a Python list for simplicity
    """

    def __init__(self) -> None:
        # regs[i] corresponds to register xi (0–31).
        # Start with all registers = 0.
        self._regs: List[int] = [0] * NUM_REGS

    # --------------------------------------------------------
    # Reset logic
    # --------------------------------------------------------
    def reset(self) -> None:
        """
        Reset all registers (except x0) to zero.

        x0 is already 0 and stays 0 forever per RISC-V spec.
        """
        for i in range(1, NUM_REGS):
            self._regs[i] = 0

    # --------------------------------------------------------
    # Register read
    # --------------------------------------------------------
    def read(self, idx: int) -> int:
        """
        Read the value of register x[idx].

        Always returns the masked 32-bit value.
        """
        _check_idx(idx)
        return _mask32(self._regs[idx])

    # --------------------------------------------------------
    # Register write
    # --------------------------------------------------------
    def write(self, idx: int, value: int, we: bool = True) -> None:
        """
        Write 'value' to register x[idx] if write-enable is True.

        • Writes to x0 (idx = 0) are ignored — required by spec.
        • All written values are masked to 32 bits.
        """
        if not we:
            return

        _check_idx(idx)

        if idx == 0:
            # Software attempting to modify x0 should have no effect.
            return

        self._regs[idx] = _mask32(value)

    # --------------------------------------------------------
    # Debugging helper
    # --------------------------------------------------------
    def dump(self) -> list[int]:
        """
        Return a copy of all register values.

        Useful for:
        • Debug output
        • Test suites validating full CPU state
        """
        return list(self._regs)
