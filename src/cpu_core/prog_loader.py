# src/cpu_core/prog_loader.py
from typing import List

def load_prog_hex(path: str) -> List[int]:
    words: List[int] = []

    with open(path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            # Strip whitespace from both ends
            text = line.strip()
            if not text:
                # Skip completely empty lines
                continue

            # Remove comments that start with '#' or '//'
            if "#" in text:
                text = text.split("#", 1)[0].strip()
            if "//" in text:
                text = text.split("//", 1)[0].strip()

            if not text:
                # Line only had a comment
                continue

            # Remove optional 0x prefix
            if text.startswith("0x") or text.startswith("0X"):
                text = text[2:]

            # Remove underscores if the file uses grouping like 0000_0000
            text = text.replace("_", "")

            if not text:
                # Nothing left after cleaning; skip
                continue

            try:
                value = int(text, 16)
            except ValueError as e:
                raise ValueError(f"Invalid hex value on line {lineno}: {line!r}") from e

            # Ensure the value is treated as a 32-bit word
            value &= 0xFFFF_FFFF
            words.append(value)

    return words
