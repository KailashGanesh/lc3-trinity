#include <stdint.h>
// bitwise operation takes number 1 0000 0000 0000 0001 and shifts it to the left by 16 bits
// Shifting left by 16 positions is equivalent to multiplying by 2^16
#define MEMORY_MAX (1 << 16)

uint16_t memory[MEMORY_MAX];

// registers - LC-3 has 10 total registers
// - 8 general purpose registers (R0-R7)
// - 1 program counter (PC) register
// - 1 condition flags (COND) register
enum
{
    R_R0 = 0,
    R_R1,
    R_R2,
    R_R3,
    R_R4,
    R_R5,
    R_R6,
    R_R7,
    R_PC,
    R_COND,
    R_COUNT
};

uint16_t reg[R_COUNT];

enum
{
    OP_BR = 0,
    OP_ADD,
    OP_LD,
    OP_ST,
    OP_JSR,
    OP_AND,
    OP_LDR,
    OP_STR,
    OP_RTI,
    OP_NOT,
    OP_LDI,
    OP_STI,
    OP_JMP,
    OP_RES,
    OP_LEA,
    OP_TRAP
};

// Condition flags - the LC-3 uses 3 conditions

enum
{
    FL_POS = 1 << 0,
    FL_ZRO = 1 << 1,
    FL_NEG = 1 << 2,
};

int main(int argc, const char* argv[]){
  @{Load Arguments}
  @{setup}

  /* one condition flag needs to be set at any given time*/
    reg[R_COND] = FL_ZRO;

  /* set the PC to starting positon */
  /* 0x3000 is the default */
  enum { PC_START = 0x3000 };
  reg[R_PC] = PC_START;

  int running = 1;
  while (running){
    uint16_t instr = mem_read(reg[R_PC]++);
    uint16_t op = instr >> 12;

    switch (op){
      case OP_ADD:
        @{ADD}
        break;
      case OP_AND:
        @{AND}
        break;
      case OP_NOT:
        @{NOT}
        break;
      case OP_BR:
        @{BR}
        break;
      case OP_JMP:
        @{JMP}
        break;
      case OP_JSR:
        @{JMR}
        break;
      case OP_LD:
        @{LD}
        break;
      case OP_LD:
        @{LD}
        break;

    }
  }
}
