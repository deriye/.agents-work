# Registers

Most CPUs have a number of registers which store small amounts of data that the CPU is processing. In our simple breadboard CPU, we'll build three 8-bit registers: A, B, and IR. The A and B registers are general-purpose registers. IR (the instruction register) works similarly, but we'll only use it for storing the current instruction that's being executed.