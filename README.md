Amount of instructions: 43 (ranging from 0x00 to 0x2A)

## Introduction
- `pyasm` is a custom assembly language that runs on Python script.
- `rodata` is address pointers list which data on them is read-only (limit: 0xFFFF).
- `bss` is another address pointers list which data on them is read/write (limit: 0xFFFF).
- `buffers` are buffers stored in `CPU` (`A`, `B`, `X`, etc), you can use them as buffer slots.
- `PC` is the program counter.
- `code` is a list where your code will run, please remember that every index counts as an entire `PC` step. Some instructions take up more than 1 byte of `code` (which `PC` will then step forward more than 1 step).
- The `CPU` is simulated (VM) that is protected (meaning once something is off, it reports the error and stops its code), it's currently 8-bit.
- The `PPU` (Picture Processing Unit) is like GPU that has resolution of 256x256 pixels, where you can draw things (there is now color support for a single 8-bit byte, with color palette for sprites).

## The checker
The checker is the one that checks if you set up `rodata` and `bss` structure correctly, by checking the following for each of item index in both of them:
1. if `"size"` is not 0x0.
2. if `"data"` fits withn `rodata_size` or `bss_size` and isn't out of bounds.
3. if `"data"` doesn't overlap next address pointer.
4. if `"size"` value is equal or larger than actual data's size.
5. (for val) if the value is withn 8-bit limit.
6. (for val) warn if `"size"` has unused occupied space.
7. etc

If one of them fails, it reports error and moves on to next item index.

## Your `pyasm` code
This will assume that you already know about hex values.\
At `code` list, you can write code in hex bytes.\
For example here's the classic hello world code:
```python
rodata = {
    0x0: { # hw_msg
        "addr": 0x0000,
        "sprite": False,
        "data": "Hello, World!",
        "size": 0xD
    },
}

bss = {
    0x0: { # empty_var
        "addr": 0x0000,
        "data": 0x00,
        "size": 0x1
    },
}

code = [
    ## main: 0x00
        0x00, 0x00, 0x0000, # 0x00: LDA rodata hw_msg
        0x0A, 0x00,         # 0x03: OUT A
        0x1F,               # 0x05: HLT
]
```

When you run it with `debug_mode` turned on, you get output that looks like this (ignore PPU window pop-up for this example):
```
debug: ran instruction 0x0 (LDA) at PC=0x0
debug: compare status 0x0
debug: pen active 0x0
debug: A  = Hello, World!
debug: B  = 0x0
debug: X  = 0x0
debug: Y  = 0x0
debug: PC = 0x3
debug: ran instruction 0xa (OUT) at PC=0x3
Hello, World!
debug: compare status 0x0
debug: pen active 0x0
debug: A  = Hello, World!
debug: B  = 0x0
debug: X  = 0x0
debug: Y  = 0x0
debug: PC = 0x5
debug: ran instruction 0x1f (HLT) at PC=0x5
```

Pretty cool, right?

## Learning about instructions
You've noticed there's a file named `instructions list.txt`.\
That text file has all information on instructions on what they do and what arguments they need.

## How to run your 'pyasm' code
1. Install Python (recommended version 3.11.9): https://www.python.org/downloads/
2. Run `install-packages.bat` file to install required package(s).
3. Run `pyasm.py` file by opening it or running it on terminal.

## Sprites
Read `\sprites\making-sprites.txt` file for info.
