# LC-3 CPU building notes

## Memory of LC-3
- The address bus of LC-3 is designed to use 16 bit memory address, which means memory is identified with a unique 16 bit number; because of this the address bus (the wires from CPU to the RAM stick) is 16 wires
- each of these wires, can be 1 or 0

so, we can use rule of product to find the total number of memory locations:

$$(\text{2 states per wire})^{16 \text{ wires}} = 65,536 \text{ locations}$$

Memory table will look like this:

| Memory Address (Hex) | Memory Address (Decimal) | Binary Representation | Data Stored (Example) |
| :--- | :--- | :--- | :--- |
| `x0000` | 0 | `0000000000000000` | `xFD70` |
| `x0001` | 1 | `0000000000000001` | `x1248` |
| `x0002` | 2 | `0000000000000010` | `x300A` |
| ... | ... | ... | ... |
| `xFFFF` | 65,535 | `1111111111111111` | `xABCD` |


The best way I know how to write code, is to try to implement a mini thing, and
though this process you build the whole machine -- or in some cases you
implement exactly what you need and nothing more 
which can be good in some cases

So I want to implement ADD function
but all CPUs need to HAULT, so let's implement HALUT first
we also need a HALUT program to run, to test this
So, I'll build one in `tests/`
then I'll write the `.obj` reader in python


- https://realpython.com/python-bitwise-operators/
- http://lc3tutor.org/
- https://github.com/chiragsakhuja/lc3tools/tree/master
- https://github.com/rpendleton/lc3-2048
- https://www.jmeiners.com/lc3-vm/#assembly-examples