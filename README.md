# RISC-V Numeric Ops Simulator  
### CPSC 440 – Midterm Alternative Project

This project implements a simulation of the core **numeric operations** of the RISC-V RV32I, RV32M, and IEEE-754 Float32 instruction subsets.  
All operations are performed on **bit-vectors**, using only the logic permitted by the assignment (no use of Python’s built-in bitwise operators for arithmetic).

The project includes:  
- Manual bit-vector utilities  
- Ripple-carry adders  
- Logical and arithmetic shifters  
- 32-bit two’s-complement encode/decode  
- RV32I ADD/SUB with NZCV flags  
- RV32M MUL/DIV/REM operations  
- IEEE-754 float32 packing, unpacking, add, sub, and mul  
- A complete unit tests covering all edge cases

--- 

## **Project Structure**

rv-numeric-sim/
├─ src/
│ ├─ numeric_core/
│ │ ├─ init.py
│ │ ├─ bits.py
│ │ ├─ adders.py
│ │ ├─ shifter.py
│ │ ├─ twos.py
│ │ ├─ alu.py
│ │ ├─ mdu.py
│ │ ├─ fpu_f32.py
│ │ └─ trace.py
│ └─ ...
├─ tests/
│ ├─ test_bits.py
│ ├─ test_twos.py
│ ├─ test_alu.py
│ ├─ test_mdu.py
│ └─ test_fpu_f32.py
├─ README.md
├─ AI_USAGE.md
└─ ai_report.json

## **Module Overview**

### `bits.py`  
- Basic bit types (`Bit`, `Bits`)  
- Zero-padding, ones/zeros utilities  
- Manual uint - bit-vector conversion  
- Manual hex formatting (no built-ins)

### `adders.py`
- Half adder  
- Full adder  
- 32-bit ripple-carry add  
- Bitwise invert  
- Two’s-complement negate

### `shifter.py`
- SLL, SRL, SRA via list operations only

### `twos.py`
- Encode/decode 32-bit two’s-complement  
- Overflow detection  
- Sign-extend and zero-extend

### `alu.py`
- ADD and SUB  
- NZCV flag computation

### `mdu.py`
- RV32M signed/unsigned multiply  
- High/low 32-bit results  
- Signed/unsigned division and remainder  
- Correct RISC-V semantics for:
  - divide-by-zero  
  - INT_MIN / −1  
  - truncation toward zero  

### `fpu_f32.py`
- IEEE-754 float32 pack/unpack  
- 1-bit sign, 8-bit exponent, 23-bit fraction  
- fadd, fsub, fmul  
- Correct normalization and basic rounding  
- Matching hex results for known values (3.75, 0.75, 3.0, etc.)

### `trace.py`
- Simple helpers for formatting debug rows  
- Useful for extended testing or visualization

---

## **Running the Tests**

All tests use `pytest`.

### Install dependencies:
pip install pytest