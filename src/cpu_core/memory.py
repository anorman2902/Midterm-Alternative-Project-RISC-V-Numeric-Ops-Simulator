from typing import List

XLEN = 32

# ----------------------------------------
# Basic safety checks for memory accesses
# ----------------------------------------
def _check_aligned(addr: int) -> None:
    """Ensure the address is 4-byte aligned (required for word access)."""
    if addr % 4 != 0:
        raise ValueError(f"Unaligned word access at address 0x{addr:08X}")


def _check_index(idx: int, size: int) -> None:
    """Ensure the computed word index is inside the memory array."""
    if not (0 <= idx < size):
        raise IndexError(f"Memory index out of range: {idx} (size={size})")


def _mask32(value: int) -> int:
    """Force values to 32-bit word size."""
    return value & 0xFFFF_FFFF


# ============================================================
# Simple word-addressable memory model for the CPU datapath
# ============================================================
class Memory:
    def __init__(self, num_words: int) -> None:
        """
        Initialize memory with a fixed number of *words* (not bytes).
        Each entry holds a 32-bit word.
        """
        if num_words <= 0:
            raise ValueError("num_words must be positive")
        self._size = num_words
        self._data: List[int] = [0] * num_words

    def reset(self, value: int = 0) -> None:
        """Fill memory with a repeated 32-bit value."""
        v = _mask32(value)
        for i in range(self._size):
            self._data[i] = v

    # ----------------------------------------
    # Word load/store operations
    # ----------------------------------------
    def load_word(self, addr: int) -> int:
        """Load a 32-bit word from an aligned address."""
        _check_aligned(addr)
        idx = addr // 4
        _check_index(idx, self._size)
        return _mask32(self._data[idx])

    def store_word(self, addr: int, value: int) -> None:
        """Store a 32-bit word at an aligned address."""
        _check_aligned(addr)
        idx = addr // 4
        _check_index(idx, self._size)
        self._data[idx] = _mask32(value)

    # ============================================================
    # AI-BEGIN
    # Non-trivial section: program loading.
    # Must safely copy a list of words into memory while enforcing
    # alignment and bounds, mirroring how real CPU loaders behave.
    # ============================================================
    def load_program(self, words: List[int], base_addr: int = 0) -> None:
        """Load a list of 32-bit words into memory starting at base_addr."""
        _check_aligned(base_addr)
        start_idx = base_addr // 4

        if start_idx + len(words) > self._size:
            raise IndexError(
                f"Program of {len(words)} words does not fit starting at "
                f"index {start_idx} in memory of size {self._size}"
            )

        for i, w in enumerate(words):
            self._data[start_idx + i] = _mask32(w)
    # AI-END
    # ============================================================

    def dump_words(self) -> List[int]:
        """Return a full copy of the memory array (useful for debugging)."""
        return list(self._data)
