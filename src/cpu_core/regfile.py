# src/cpu_core/regfile.py
from typing import List


NUM_REGS = 32
XLEN = 32


def _check_idx(idx: int) -> None:
    """Simple bounds check for a register index."""
    if not (0 <= idx < NUM_REGS):
        raise IndexError(f"Register index out of range: {idx}")

def _mask32(value: int) -> int:
    """Mask a Python int down to 32 bits."""
    return value & 0xFFFF_FFFF


class RegFile:
    """Simple 32-register file with x0 hardwired to zero."""

    def __init__(self) -> None:
        # Use a plain Python list of ints to store register values.
        # regs[0] corresponds to x0, regs[1] to x1, ..., regs[31] to x31.
        self._regs: List[int] = [0] * NUM_REGS

    def reset(self) -> None:
        """Reset all registers to 0 (x0 is already 0)."""
        for i in range(1, NUM_REGS):
            self._regs[i] = 0

    def read(self, idx: int) -> int:
        """
        Read the value of register x[idx].
        Always returns a 32-bit value.
        """
        _check_idx(idx)
        # x0 is stored as 0, so no special case is needed here.
        return _mask32(self._regs[idx])

    def write(self, idx: int, value: int, we: bool = True) -> None:
        """
        Write 'value' to register x[idx] if write enable is True.
        Writes to x0 (idx == 0) are ignored to enforce x0 == 0.
        """
        if not we:
            return
        _check_idx(idx)
        if idx == 0:
            # Ignore writes to x0 (it must always stay 0).
            return
        self._regs[idx] = _mask32(value)


    def dump(self) -> list[int]:
        """
        Return a copy of the internal register list.
        Useful for debugging or tests that want to inspect all registers.
        """
        return list(self._regs)
