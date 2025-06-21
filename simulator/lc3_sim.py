import sys
from enum import IntEnum

def make_nibbles(word):
    """Takes 16 bit word, and give you an List with 4 bit chunks"""
    nibbles = []
    for i in range(4):
        shift = i * 4
        chunk = word >> shift & 0xF
        nibbles.insert(0,chunk)
    return nibbles

class Opcodes(IntEnum):
   # Control Instructions
    BR = 0x0       # Branch
    JMP = 0xC      # Jump (includes RET)
    JSR = 0x4      # Jump to Subroutine (includes JSRR)
    RTI = 0x8      # Return from Interrupt
    TRAP = 0xF     # System Call

    # Operate Instructions
    ADD = 0x1      # Add
    AND = 0x5      # Bitwise AND
    NOT = 0x9      # Bitwise NOT

    # Data Movement Instructions
    LD = 0x2       # Load
    LDI = 0xA      # Load Indirect
    LDR = 0x6      # Load Base+Offset
    LEA = 0xE      # Load Effective Address
    ST = 0x3       # Store
    STI = 0xB      # Store Indirect
    STR = 0x7      # Store Base+Offset
    
    # Reserved Opcode
    RESERVED = 0xD # This opcode is unused

class LC3_VM:
    def __init__(self):
        # Memory
        self.memory = [0] * (2**16)

        # Registers 
        self.registers = {
            "R0": 0,
            "R1": 0,
            "R2": 0,
            "R3": 0,
            "R4": 0,
            "R5": 0,
            "R6": 0,
            "R7": 0,
            "PC": 0x3000,
            "COND": 0,
        }

        self.running = True

    def dump(self):
        for i in self.registers.keys():
            nibbles = make_nibbles(self.registers[i])
            print(f"{i}: {nibbles[0]:04b} {nibbles[1]:04b} {nibbles[2]:04b} {nibbles[3]:04b}")
    
    def run(self):
        self.memory[0x3000] = 0xF025
        while self.running:
            self.dump()
            # 1. Fetch
            current_instruction = self.memory[self.registers["PC"]]

            # 2. Increment Program counter
            self.registers["PC"] += 1

            # 3. Decode & Execute
            opcode = current_instruction >> 12

            match opcode:
                case 0xF:
                    print("TRAP")
                    trapvect8 = current_instruction & 0xFF
                    if trapvect8 == 0x25: 
                        print("HAULT")
                        self.running = False
                case 0x5:
                    print("AND")
                case 0x1:
                    if current_instruction >> 4 & 0b1 == 0:
                        print("DR = SR1 + SR2;")
                        pass
                    else:
                        print("DR = SR1 + SEXT(imm5);")
                        pass

vm = LC3_VM()
vm.run()