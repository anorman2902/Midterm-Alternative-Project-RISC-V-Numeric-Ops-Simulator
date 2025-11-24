# RISC-V Single-Cycle CPU Simulator  
### CPSC 440 — The Default

This project implements a **single-cycle RV32I CPU** in Python.  
The CPU supports a meaningful subset of the RISC-V base instruction set, runs real 32-bit program images (`prog.hex`), and passes a full unit test suite validating arithmetic, branching, memory, and control-flow behavior.

---

## Project Structure

```txt
src/
├── cpu_core/
│   ├── control.py        # opcode/funct3/funct7 decode → control signals
│   ├── datapath.py       # single-cycle CPU datapath implementation
│   ├── isa.py            # enum-like constants & helpers for instruction fields
│   ├── memory.py         # word-addressable instruction & data memory
│   ├── prog_loader.py    # .hex program loader
│   ├── regfile.py        # 32 × 32-bit register file (x0 hardwired to 0)
│   └── run_cpu.py        # CLI entry point
│
├── numeric_core/         # (Separate project — midterm assignment)
│   └── ...
│
tests/
│   ├── test_cpu_base.py
│   ├── test_cpu_arith.py
│   ├── test_cpu_arith_logic.py
│   ├── test_cpu_branch_mem.py
│   └── programs/
│       ├── prog.hex
│       └── test_base.hex
│
README.md
AI_USAGE.md
ai_report.json
```

---

# CPU Architecture Overview

## Single-Cycle Datapath

Every instruction is fetched, decoded, executed, and written back in **one clock cycle**.  
The datapath includes:

- Program Counter (PC)  
- Instruction Memory (IMEM)  
- Register File (x0–x31)  
- Immediate Generator  
- ALU (ADD, SUB, logic ops, shifts)  
- Branch Comparator  
- Data Memory (DMEM)  
- Control Unit (opcode / funct3 / funct7 decoding)

### Execution Flow

PC → IMEM → Decode → Control
↘→ RegFile → ALU → Branch Logic
↘→ DMEM → Writeback → RegFile
PC ← Branch/Jump Target or PC + 4


---

# Supported Instruction Set (RV32I Subset)

### **R-type**
- ADD, SUB  
- AND, OR, XOR  
- SLL, SRL, SRA  
- SLT, SLTU  

### **I-type**
- ADDI, ANDI, ORI, XORI  
- SLLI, SRLI, SRAI  
- LW  
- JALR  

### **S-type**
- SW  

### **B-type**
- BEQ, BNE  
- BLT, BGE  
- BLTU, BGEU  

### **U-type**
- LUI  
- AUIPC  

### **J-type**
- JAL  

This instruction coverage matches all operations used in the test programs and satisfies the “meaningful subset” requirement.

---

#  Program Loading (.hex)

The CPU loads programs written in the assignment-required format:

- One 32-bit hex word per line  
- No `0x` prefix  
- Blank lines allowed  
- Comments allowed (`#` or `//`)

Example (`prog.hex`):

00500093
00A00113
002081B3


Load and run a program via Python:

```python
from src.cpu_core.run_cpu import run_program
cpu = run_program("tests/programs/prog.hex")

Running the CPU & Tests
Install Dependencies

    pip install pytest

Run All Tests

    pytest -q

The test suite validates:

- Arithmetic & logic operations

- Shifts

- Memory load/store

- Branch conditions

- Jumps (jal, jalr)

- Integration via prog.hex

Run a Program Manually

    python -m src.cpu_core.run_cpu tests/programs/prog.hex

Design Notes
Control Unit

- Decodes opcode, funct3, funct7

- Produces control signals for ALU operation

- Selects immediate type

- Determines branching behavior

- Controls memory read/write

- Controls PC update on branches & jumps

ALU

Supports:

    ADD / SUB

    AND / OR / XOR

    SLL / SRL / SRA

    SLT / SLTU

    All shift and logic ops used in test programs

Memory

    Word-aligned memory

    32-bit loads/stores

    Out-of-bounds and unaligned accesses are rejected for safety

Register File

    32 × 32-bit registers

    Two read ports, one write port

    Writes to x0 are ignored (RISC-V spec)

    Block Diagram

             +--------------------+
             |    Instruction     |
      PC --->|      Memory        |
             +---------+----------+
                       |
                       v
                 +-----------+
                 |  Decode   |
                 +-----+-----+
                       |
     +-----------------+------------------+
     |                                    |
     v                                    v
+----------+                        +-----------+
| RegFile  |                        | Immediate |
| x0-x31   |                        | Generator |
+----+-----+                        +-----+-----+
     |                                    |
     +-------------------+----------------+
                         |
                         v
                    +---------+
                    |   ALU   |
                    +---------+
                         |
                 +-------+-------+
                 |               |
                 v               v
              Data Mem       Branch/Jump
                 |            Decision
                 v               |
                WB <-------------+
                 |
                 v
          Writeback to RegFile

## Test Results

All CPU tests pass successfully.

## Pytest Output
..................................                                                                                                                                                                                                                                                                                                                                                                 [100%]
34 passed in 0.13s


AI Usage Disclosure

    See AI_USAGE.md for the complete AI usage log.

    AI-generated code and suggestions incorporated into source files are marked using:

    # AI-BEGIN
    # AI-END
All AI suggestions were reviewed and integrated manually.