# LC-3 CPU


```
lc3_project/
├── simulator/          # C or python implementation
├── hardware/           # Verilog implementation  
├── assembler/          # my own assembler
└── programs/           # Test programs
    ├── hello_world.asm
    └── fibonacci.asm
```

## what I learned:
- when I first started this in C, I have no clue what registers referes to, what op codes are; even though I have used a shift register + 556 timer to make a LED chaser in the past
- I watched [Ben Easter's Programming my 8-bit breadboard computer video](https://www.youtube.com/watch?v=9PPrrSyubG0) and every thing makes sense now - even though his CPU is SAP-1 based; seeing physical registers and manually programming the computer made the concepts click.
- I decided to start writing it in python first because I have a better understanding of the language and it's easier to debug. then move to C.

## Resources:
- [LC-3 ISA](https://www.cs.colostate.edu/~cs270/.Spring23/resources/PattPatelAppA.pdf)
- [Write your Own Virtual Machine ](https://www.jmeiners.com/lc3-vm/)
- [Writing a simple 16 bit VM in less than 125 lines of C](https://www.andreinc.net/2021/12/01/writing-a-simple-vm-in-less-than-125-lines-of-c)