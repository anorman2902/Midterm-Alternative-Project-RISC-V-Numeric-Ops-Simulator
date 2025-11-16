# src/numeric_core/trace.py
from typing import List

# build header line for trace output
def header(cols: List[str]) -> str:
    return ' | '.join(cols)

# build one row for trace output
def row(values: List[str]) -> str:
    return ' | '.join(values)
