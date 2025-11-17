# src/cpu_core/memory.py
from typing import List

XLEN = 32

def _check_aligned(addr: int) -> None:
    if addr % 4 != 0:
        raise ValueError(f"Unaligned word access at address 0x{addr:08X}")


def _check_index(idx: int, size: int) -> None:
    if not (0 <= idx < size):
        raise IndexError(f"Memory index out of range: {idx} (size={size})")


def _mask32(value: int) -> int:
    return value & 0xFFFF_FFFF


class Memory:
    def __init__(self, num_words: int) -> None:
        if num_words <= 0:
            raise ValueError("num_words must be positive")
        self._size = num_words
        self._data: List[int] = [0] * num_words

    def reset(self, value: int = 0) -> None:
        v = _mask32(value)
        for i in range(self._size):
            self._data[i] = v

    def load_word(self, addr: int) -> int:
        _check_aligned(addr)
        idx = addr // 4
        _check_index(idx, self._size)
        return _mask32(self._data[idx])

    def store_word(self, addr: int, value: int) -> None:
        _check_aligned(addr)
        idx = addr // 4
        _check_index(idx, self._size)
        self._data[idx] = _mask32(value)

    def load_program(self, words: List[int], base_addr: int = 0) -> None:
        _check_aligned(base_addr)
        start_idx = base_addr // 4

        if start_idx + len(words) > self._size:
            raise IndexError(
                f"Program of {len(words)} words does not fit starting at "
                f"index {start_idx} in memory of size {self._size}"
            )

        for i, w in enumerate(words):
            self._data[start_idx + i] = _mask32(w)


    def dump_words(self) -> List[int]:
        return list(self._data)
