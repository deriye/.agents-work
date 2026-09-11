# CPU control logic

The control logic is the heart of the CPU. It's what defines the opcodes the processor recognizes and what happens when it executes each instruction.

### Videos

- 8-bit CPU control logic: Part 1
- 8-bit CPU control logic: Part 2
- 8-bit CPU control logic: Part 3
- 8-bit CPU reset circuit and power supply tips
- Reprogramming CPU microcode with an Arduino
- Adding more machine language instructions to the CPU
- Making a computer Turing complete
- CPU flags register
- Conditional jump instructions

### Notes

An alternative to soldering a USB cable for power is to use a [DC wall plug](http://bit.ly/2Tz66rQ) with a [screw terminal adapter](http://bit.ly/2SAGj54) (If you bought [Kit #1](https://eater.net/8bit/kits) from me, you already have these). To create a more robust connection as described in the video above about power supply tips, you can use multiple wires like this:

[[power-connection.png]]

Schematic

[[schematic.png]]

Also see the flags register part of the [ALU schematic](https://eater.net/8bit/alu).

### Data sheets

- 74LS00 Quad NAND gate
- 74LS04 Hex inverter
- 74LS161 4-bit binary counter
- 74LS138 3-to-8 line decoder/demultiplexer
- 28C16 16K EEPROM