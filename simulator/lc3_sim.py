from enum import Flag, IntEnum


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
    RTI = 0x8  # Return from Interrupt
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
            "R2": 0x0005,
            "R3": 0x000A,
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
            # is_negative = imm5 >> 4 & 0b1

            # if is_negative:
            #     imm5 = imm5 | 0xFFE0

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
            # is_negative = imm5 >> 4 & 0b1
            # if is_negative:
            #     imm5 = imm5 - 32  # 2^5 = 32
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

        # if (PCoffset9 >> 8) & 1:
        #     PCoffset9 |= 0xFE00

        # result = self.registers["PC"] + PCoffset9 & 0xFFFF
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

        # if (PCoffset9 >> 8) & 1:
        #     PCoffset9 |= 0xFE00

        # first_address = self.registers["PC"] + PCoffset9 & 0xFFFF
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

        # if (offset6 >> 5) & 1:
        #     offset6 |= 0xFFC0

        # self.registers[DR] = self.memory[
        #     self.registers[BaseR] + offset6 & 0xFFFF
        # ]

        self.registers[DR] = self.memory[
            (self.registers[BaseR] + sign_extend(offset6, 6)) & 0xFFFF
        ]
        self.update_cond_flag(self.registers[DR])

    def op_lea(self, current_instruction):
        DR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        # if (PCoffset9 >> 8) & 1:
        #     PCoffset9 |= 0xFE00

        # self.registers[DR] = self.registers["PC"] + PCoffset9 & 0xFFFF
        self.registers[DR] = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF
        self.update_cond_flag(self.registers[DR])

    def op_st(self, current_instruction):
        SR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        # if (PCoffset9 >> 8) & 1:
        #     PCoffset9 |= 0xFE00

        result = (self.registers["PC"] + sign_extend(PCoffset9, 9)) & 0xFFFF

        if result < 0x3000:
            print("Not Allowed")
            self.running = False
        else:
            self.memory[result] = self.registers[SR]

    def op_sti(self, current_instruction):
        SR = "R" + str(current_instruction >> 9 & 0b111)
        PCoffset9 = current_instruction & 0x1FF

        # if (PCoffset9 >> 8) & 1:
        #     PCoffset9 |= 0xFE00

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

        # if (offset6 >> 5) & 1:
        #     offset6 |= 0xFFC0

        self.memory[(self.registers[BaseR] + sign_extend(offset6, 6)) & 0xFFFF] = (
            self.registers[SR]
        )

    def op_ret(self, current_instruction):
        self.registers["PC"] = self.registers["R7"]

    def op_rti(self, current_instruction):
        if PSR[15] == 0:
            self.registers["PC"] = self.memory[self.registers["R6"]]
            self.registers["R6"] += 1
            TEMP = self.memory[self.registers["R6"]]
            self.registers["R6"] += 1
            PSR = TEMP
        else:
            print("RTI not allowed in user mode")
            self.running = False

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

                # case Opcodes.RET:
                #     self.op_ret(current_instruction)

                # case Opcodes.RTI:
                #   self.op_rti(current_instruction)

                case Opcodes.ST:
                    self.op_st(current_instruction)

                case Opcodes.STI:
                    self.op_sti(current_instruction)

                case Opcodes.STR:
                    self.op_str(current_instruction)

                case _:
                    print(f"Unknown opcode: {bin(opcode)}")
                    self.running = False


if __name__ == "__main__":
    vm = LC3_VM()
    vm.run()
