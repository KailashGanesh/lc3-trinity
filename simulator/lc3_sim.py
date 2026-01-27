from enum import IntEnum


def sign_extend(value, bit_count):
    if (value >> (bit_count - 1)) & 1:
        value |= 0xFFFF << bit_count
    return value & 0xFFFF


def make_nibbles(word):
    """Takes 16 bit word, and give you an List with 4 bit chunks"""
    nibbles = []
    for i in range(4):
        shift = i * 4
        chunk = word >> shift & 0xF
        nibbles.insert(0, chunk)
    return nibbles


class Opcodes(IntEnum):
    # Control Instructions
    BR = 0x0  # Branch
    JMP = 0xC  # Jump (includes RET)
    JSR = 0x4  # Jump to Subroutine (includes JSRR)
    TRAP = 0xF  # System Call

    # Operate Instructions
    ADD = 0x1  # Add
    AND = 0x5  # Bitwise AND
    NOT = 0x9  # Bitwise NOT

    # Data Movement Instructions
    LD = 0x2  # Load
    LDI = 0xA  # Load Indirect
    LDR = 0x6  # Load Base+Offset
    LEA = 0xE  # Load Effective Address
    ST = 0x3  # Store
    STI = 0xB  # Store Indirect
    STR = 0x7  # Store Base+Offset

    # Reserved Opcode
    RTI = 0x8  # Return from Interrupt *unused*
    RESERVED = 0xD  # This opcode is unused


class ConditionFlags(IntEnum):
    P = 1 << 0
    Z = 1 << 1
    N = 1 << 2


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

    def update_cond_flag(self, result):
        # Make result into 16 bit for the sign check
        result &= 0xFFFF

        if result == 0:
            self.registers["COND"] = ConditionFlags.Z
        elif (result >> 15) & 1:
            self.registers["COND"] = ConditionFlags.N
        else:
            self.registers["COND"] = ConditionFlags.P

    def dump(self):
        for i in self.registers.keys():
            nibbles = make_nibbles(self.registers[i])
            print(
                f"{i}: {nibbles[0]:04b} {nibbles[1]:04b} {nibbles[2]:04b} {nibbles[3]:04b}"
            )

    def op_trap(self, current_instruction):
        trapvect8 = current_instruction & 0xFF
        if trapvect8 == 0x25:
            self.running = False

    def op_and(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        SR1 = "R" + str(current_instruction >> 6 & 0b111)

        if current_instruction >> 5 & 0b1 == 0:
            SR2 = "R" + str(current_instruction & 0b111)
            self.registers[DR] = self.registers[SR1] & self.registers[SR2]
        else:
            imm5 = current_instruction & 0b11111

            self.registers[DR] = self.registers[SR1] & sign_extend(imm5, 5)

        self.update_cond_flag(self.registers[DR])

    def op_add(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        SR1 = "R" + str(current_instruction >> 6 & 0b111)

        if current_instruction >> 5 & 0b1 == 0:
            SR2 = "R" + str(current_instruction & 0b111)
            result = self.registers[SR1] + self.registers[SR2]
        else:
            imm5 = current_instruction & 0b11111
            result = self.registers[SR1] + sign_extend(imm5, 5)

        self.registers[DR] = result & 0xFFFF
        self.update_cond_flag(self.registers[DR])

    def op_not(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        SR = "R" + str(current_instruction >> 6 & 0b111)

        self.registers[DR] = self.registers[SR] ^ 0xFFFF

        self.update_cond_flag(self.registers[DR])

    def op_ld(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        result = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF

        if result < 0x3000:
            print("Not Allowed")
            self.running = False
        else:
            self.registers[DR] = self.memory[result]
            self.update_cond_flag(self.registers[DR])

    def op_ldi(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        first_address = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF

        value = self.memory[self.memory[first_address]]

        if first_address < 0x3000 and value < 0x3000:
            print("Not Allowed")
            self.running = False

        else:
            self.registers[DR] = value

            self.update_cond_flag(self.registers[DR])

    def op_ldr(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        BaseR = "R" + str(current_instruction >> 6 & 0b111)
        offset6 = current_instruction & 0b111111

        self.registers[DR] = self.memory[
            (self.registers[BaseR] + sign_extend(offset6, 6)) & 0xFFFF
        ]
        self.update_cond_flag(self.registers[DR])

    def op_lea(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        self.registers[DR] = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF
        self.update_cond_flag(self.registers[DR])

    def op_st(self, current_instruction):
        SR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        result = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF

        if result < 0x3000:
            print("Not Allowed")
            self.running = False
        else:
            self.memory[result] = self.registers[SR]

    def op_sti(self, current_instruction):
        SR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        first_address = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF
        result = self.memory[first_address]
        if first_address < 0x3000 and result < 0x3000:
            print("Not Allowed")
        else:
            self.memory[result] = self.registers[SR]

    def op_str(self, current_instruction):
        SR = "R" + str(current_instruction >> 9 & 0b111)
        BaseR = "R" + str(current_instruction >> 6 & 0b111)
        offset6 = current_instruction & 0b111111

        self.memory[(self.registers[BaseR] + sign_extend(offset6, 6)) & 0xFFFF] = (
            self.registers[SR]
        )

    def op_jmp(self, current_instruction):
        """RET is just JMP but with PC = R7 always"""
        BaseR = (current_instruction >> 6) & 0b111  # number of registor
        BaseR = "R" + str(BaseR)  # needs to be a registor name
        self.registers["PC"] = self.registers[BaseR]

    def op_jsr(self, current_instruction):
        TEMP = self.registers["PC"]
        bit_11 = (current_instruction >> 11) & 0b1

        if bit_11 == 0b0:
            # JSRR - BaseR mode
            BaseR = (current_instruction >> 6) & 0b111
            BaseR = "R" + str(BaseR)
            self.registers["PC"] = self.registers[BaseR]
        else:
            # JSR - PCoffset11 mode
            PCoffset11 = current_instruction & 0x7FF
            self.registers["PC"] = (
                self.registers["PC"] + sign_extend(PCoffset11, 11)
            ) & 0xFFFF

        self.registers["R7"] = TEMP

    def op_br(self, current_instruction):
        PCoffset9 = current_instruction & 0x1FF
        p = (current_instruction >> 9) & 0b1
        z = (current_instruction >> 10) & 0b1
        n = (current_instruction >> 11) & 0b1

        if (
            (n and self.registers["COND"] == ConditionFlags.N)
            or (z and self.registers["COND"] == ConditionFlags.Z)
            or (p and self.registers["COND"] == ConditionFlags.P)
        ):
            self.registers["PC"] = (
                self.registers["PC"] + sign_extend(PCoffset9, 9)
            ) & 0xFFFF

    def run(self):
        while self.running:
            # self.dump()
            # 1. Fetch
            current_instruction = self.memory[self.registers["PC"]]

            # 2. Increment Program counter
            self.registers["PC"] += 1

            # 3. Decode & Execute
            opcode = current_instruction >> 12

            match opcode:
                case Opcodes.TRAP:
                    self.op_trap(current_instruction)

                case Opcodes.AND:
                    self.op_and(current_instruction)

                case Opcodes.ADD:
                    self.op_add(current_instruction)

                case Opcodes.NOT:
                    self.op_not(current_instruction)

                case Opcodes.LD:
                    self.op_ld(current_instruction)

                case Opcodes.LDI:
                    self.op_ldi(current_instruction)

                case Opcodes.LDR:
                    self.op_ldr(current_instruction)

                case Opcodes.LEA:
                    self.op_lea(current_instruction)

                case Opcodes.JMP:
                    pass


                case Opcodes.ST:
                    self.op_st(current_instruction)

                case Opcodes.STI:
                    self.op_sti(current_instruction)

                case Opcodes.STR:
                    self.op_str(current_instruction)

                case Opcodes.BR:
                    self.op_br(current_instruction)

                case _:
                    print(f"Unknown opcode: {bin(opcode)}")
                    self.running = False


if __name__ == "__main__":
    vm = LC3_VM()
    vm.run()
