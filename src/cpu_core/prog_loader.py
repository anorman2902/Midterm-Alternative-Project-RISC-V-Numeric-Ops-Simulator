from typing import List

# ----------------------------------------
# Load program from a .hex text file
# Each line represents one 32-bit instruction word.
# ----------------------------------------
def load_prog_hex(path: str) -> List[int]:
    """
    Read a hex program file and return a list of 32-bit words.
    Handles comments, blank lines, optional '0x' prefixes,
    and underscores for readability.
    """
    words: List[int] = []

    with open(path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            text = line.strip()

            # Skip empty lines early
            if not text:
                continue

            # ----------------------------------------
            # Remove inline comments (supports '#' and '//')
            # ----------------------------------------
            if "#" in text:
                text = text.split("#", 1)[0].strip()
            if "//" in text:
                text = text.split("//", 1)[0].strip()

            if not text:
                continue  # line was only a comment

            # ----------------------------------------
            # Clean optional hex formatting
            # ----------------------------------------

            # Remove 0x prefix
            if text.startswith("0x") or text.startswith("0X"):
                text = text[2:]

            # Remove underscores like "0000_0000"
            text = text.replace("_", "")

            if not text:
                continue

            # ============================================================
            # AI-BEGIN
            # Difficult section: robust hex parsing from arbitrary text.
            # Must detect invalid characters and provide helpful errors
            # with line numbers to assist debugging.
            # ============================================================
            try:
                value = int(text, 16)
            except ValueError as e:
                raise ValueError(
                    f"Invalid hex value on line {lineno}: {line!r}"
                ) from e
            # AI-END
            # ============================================================

            # Force into 32-bit word range
            value &= 0xFFFF_FFFF
            words.append(value)

    return words
