import sys
import random
import tkinter as tk

try:    #try importing all required packages
    from beep import beep
except: #otherwise, display error message instead
    print(" script error: one of packages are missing, please run 'install-packages.bat' to install all required packages (make sure you have pip installed)")
    input("press enter to exit")
    sys.exit()

## pyasm: python assembly
## created by python beginner u/windowssandbox
## mistakes in code are not noticed by me sadly (if there are any)

chk_status = False
CMP_status = False
PC = 0x0
last_JSR = []
internal_res = 256
res_scale = 3
pen_active = 0x0

#modifiers
rodata_size = 0xFFFF # (default: 0xFFFF 2kb)
bss_size    = 0xFFFF # (default: 0xFFFF 2kb)
buff_size   = 0xFF   # (default: 0xFF bytes) for each buffer
debug_mode  = 0x1    # (default: 0x0, recommended: 0x1)

#rom data
"""
    rodata is limited to 2kb ($FFFF) (extendable)
    your data goes here as read-only
    format is like this:
    <var index>: { #<var name>
        "addr": <address pointer>,
        "data": <data, value or string>,
        "size": <size>
    }
    address pointer must be valid
"""
rodata = {
    0x0: { # hw_msg
        "addr": 0x0000,
        "data": "Hello, World!",
        "size": 0xD
    },
}

#ram
"""
    bss is limited to 2kb ($FFFF) (extendable)
    your variable assignment goes here as read/write
    format is like this:
    <var index>: {
        "addr": <address pointer>,
        "data": <data, value or string>,
        "size": <size>
    }
    address pointer must be valid
"""
bss = {
    0x0: {
        "addr": 0x0000,
        "data": 0x00,
        "size": 0x1
    },
}

# your code to execute:
## it's strongly recommended that you write lines of code like this:
## <opcode>, <its arguments>, # <PC>: (instruction in text format)
## (put multiple indexes in one line)
code = [
    ## main: 0x00
        0x00, 0x00, 0x0000, # 0x00: LDA rodata hw_msg
        0x0A, 0x00,         # 0x03: OUT A
        0x1F,               # 0x05: HLT
]

#buffers
buff = { 
    "A": 0x00,
    "B": 0x00,
    "X": 0x00,
    "Y": 0x00,
}

def exit(msg=""):
    if not msg == "": print(msg)
    input("press enter to exit")
    sys.exit()

#PICTURE PROCESSING UNIT (PPU)
class PPU:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PPU")
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root,
            width  = internal_res * res_scale,
            height = internal_res * res_scale,
            bg = "black",
            highlightthickness = 0,
        )
        self.canvas.pack()
        self.pen_x    = 0x00
        self.pen_y    = 0x00
        self.pen_down = 0x0
        self.color    = "#FFFFFF"
        self.cur_line = None
    
    def on_closing(self):
        self.running = False
        self.root.destroy()
    
    def update_frame(self):
        if self.running:
            try:
                self.root.update_idletasks()
                self.root.update()
            except:
                self.running = False
    
    def set_color(self, val):
        hex_val = f"{val:02x}"
        self.color = f"#{hex_val}{hex_val}{hex_val}"
    
    def move_pen(self, x, y):
        old_x = self.pen_x
        old_y = self.pen_y
        
        if self.pen_down:
            self.canvas.create_line(
                old_x * res_scale,
                old_y * res_scale,
                x * res_scale,
                y * res_scale,
                fill = self.color,
                width = res_scale,
            )
        
        self.pen_x = x
        self.pen_y = y
    
    def clear_screen(self):
        self.canvas.delete("all")
        self.pen_x = 0
        self.pen_y = 0
        self.pen_down = 0x0

ppu = PPU()

#check for main
def chk():
    global chk_status
    if chk_status == False:
        exit()

def tryhex(data):
    try:
        return hex(data)
    except:
        return str(data)

def trylen(data):
    try:
        return len(data)
    except:
        return 1

def chk_buffers_size():
    global buff_size
    new_buff_size = 0x00
    
    As = trylen(buff["A"])
    Bs = trylen(buff["B"])
    Xs = trylen(buff["X"])
    Ys = trylen(buff["Y"])
    
    Fer = " fatal error:"
    Aem = f" {Fer} buffer A overflowed by {hex(As-buff_size)} bytes"
    Bem = f" {Fer} buffer B overflowed by {hex(Bs-buff_size)} bytes"
    Xem = f" {Fer} buffer X overflowed by {hex(Xs-buff_size)} bytes"
    Yem = f" {Fer} buffer Y overflowed by {hex(Ys-buff_size)} bytes"
    sf  = f"|SUGGESTED FIX: expand buff_size to {hex(new_buff_size)} bytes"
    
    if As <= buff_size: 0
    else: print(Aem); new_buff_size = buff_size+As; exit(sf)
    if Bs <= buff_size: 0
    else: print(Bem); new_buff_size = buff_size+Bs; exit(sf)
    if Xs <= buff_size: 0
    else: print(Xem); new_buff_size = buff_size+Xs; exit(sf)
    if Ys <= buff_size: 0
    else: print(Yem); new_buff_size = buff_size+Ys; exit(sf)

def chk_target_buffer(_buff):
    tb = "."
    em = " error: invalid target buffer"
    
    if   _buff == 0x00: tb = "A"
    elif _buff == 0x01: tb = "B"
    elif _buff == 0x02: tb = "X"
    elif _buff == 0x03: tb = "Y"
    else: exit(em)
    
    return tb

#funcs for instructions
def chk_address(loc, address):
    global rodata, bss, buff
    errors = 0
    
    if loc == 0x00:   #rodata
        for i in rodata:
            if address == rodata[i]["addr"]: return True
    
    elif loc == 0x01: #bss
        for i in bss:
            if address == bss[i]["addr"]: return True
    
    else: exit(" fatal error: invalid loc")
    
    #if it makes it to this line then it means it's not valid
    if loc == 0x00: print(f" fatal error: address {hex(address)} is not valid address inside rodata")
    if loc == 0x01: print(f" fatal error: address {hex(address)} is not valid address inside bss")
    exit()

def get_address_data(loc, address):
    global rodata, bss
    
    if loc == 0x00: #rodata
        for i in rodata:
            if address == rodata[i]["addr"]: return rodata[i]["data"]
    
    if loc == 0x01: #bss
        for i in bss:
            if address == bss[i]["addr"]: return bss[i]["data"]
    
    return 0x00

def set_address_data(data, address):
    global bss
    
    for i in bss:
        if address == bss[i]["addr"]:
            bss[i]["data"] = data
            return

def do_operator(buff1, buff2, op):
    tb1 = chk_target_buffer(buff1)
    tb2 = chk_target_buffer(buff2)
    
    if op == 0x00: return buff[tb1] == buff[tb2]
    if op == 0x01: return buff[tb1] != buff[tb2]
    if op == 0x02: return buff[tb1] >  buff[tb2]
    if op == 0x03: return buff[tb1] <  buff[tb2]
    if op == 0x04: return buff[tb1] >= buff[tb2]
    if op == 0x05: return buff[tb1] <= buff[tb2]

def val_8bit(val):
    return (val & 0xFF)

#instructions
def LDA(loc, address):  # 0x00, 2 args
    """
    loc: (
        0x00: rodata
        0x01: bss
    )
    address: <hex>
    desc: load
    """
    
    #check if that address points to valid variable
    chk_status = chk_address(loc, address)
    chk()
    
    #then load that data to buffer A
    buff["A"] = get_address_data(loc, address)

def LDB(loc, address):  # 0x01, 2 args
    """
    loc: (
        0x00: rodata
        0x01: bss
    )
    address: <hex>
    desc: load
    """
    
    #check if that address points to valid variable
    chk_status = chk_address(loc, address)
    chk()
    
    #then load that data to buffer B
    buff["B"] = get_address_data(loc, address)

def LDX(loc, address):  # 0x02, 2 args
    """
    loc: (
        0x00: rodata
        0x01: bss
    )
    address: <hex>
    desc: load
    """
    
    #check if that address points to valid variable
    chk_status = chk_address(loc, address)
    chk()
    
    #then load that data to buffer X
    buff["X"] = get_address_data(loc, address)

def STA(address):       # 0x03, 1 arg
    """
    address: <hex>
    desc: store
    """
    size_address     = bss[address]["size"]
    data_address     = bss[address]["data"]
    len_data_address = trylen(buff["A"])
    em = f" error: cannot fit string (size: {len_data_address}) inside bss {address} (size: {size_address})"
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()

    #check for string overflow
    if isinstance(buff["A"], str) and isinstance(data_address, str):
        if len_data_address <= size_address: 0
        else: exit(em)
    
    #store buffer A into that address data
    set_address_data(buff["A"], address)

def STB(address):       # 0x04, 1 arg
    """
    address: <hex>
    desc: store
    """
    size_address     = bss[address]["size"]
    data_address     = bss[address]["data"]
    len_data_address = trylen(buff["B"])
    em = f" error: cannot fit string (size: {len_data_address}) inside bss {address} (size: {size_address})"
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #check for string overflow
    if isinstance(buff["B"], str) and isinstance(data_address, str):
        if len_data_address <= size_address: 0
        else: exit(em)
    
    #store buffer B into that address data
    set_address_data(buff["B"], address)

def STX(address):       # 0x05, 1 arg
    """
    address: <hex>
    desc: store
    """
    size_address     = bss[address]["size"]
    data_address     = bss[address]["data"]
    len_data_address = trylen(buff["X"])
    em = f" error: cannot fit string (size: {len_data_address}) inside bss {address} (size: {size_address})"
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #check for string overflow
    if isinstance(buff["X"], str) and isinstance(data_address, str):
        if len_data_address <= size_address: 0
        else: exit(em)
    
    #store buffer X into that address data
    set_address_data(buff["X"], address)

def INC(_buff): # 0x06, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: increment
    """
    em  = " error: cannot increment a string"
    
    tb = chk_target_buffer(_buff)
    
    if isinstance(buff[tb], int):
        buff[tb] += 0x01
        buff[tb] = val_8bit(buff[tb])
    else: exit(em)

def DEC(_buff): # 0x07, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: decrement
    """    
    em  = " error: cannot decrement a string"
    
    tb = chk_target_buffer(_buff)
    
    if isinstance(buff[tb], int):
        buff[tb] -= 0x01
        buff[tb] = val_8bit(buff[tb])
    else: exit(em)

def ADD():      # 0x08
    """
    desc: adds value of buffer B into buffer A
    """
    em = " error: ADD cannot add strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int):
        buff["A"] += buff["B"]
        buff["A"] = val_8bit(buff["A"])
    else: exit(em)

def SUB():      # 0x09
    """
    desc: subtracts value of buffer B from buffer A
    """
    em = " error: cannot subtract strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int):
        buff["A"] -= buff["B"]
        buff["A"] = val_8bit(buff["A"])
    else: exit(em)

def OUT(_buff): # 0x0A, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: outputs data of the buffer
    """
    tb = chk_target_buffer(_buff)
    
    print(buff[tb])

def CMP(buff1, buff2, op): # 0x0B, 3 args
    """
    buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    op (
        0x00: ==
        0x01: !=
        0x02: >
        0x03: <
        0x04: >=
        0x05: <=
    )
    desc: compares buff1 <op> buff2
    """
    global CMP_status
    em1    = " error: CMP buffer1 is a string"
    em2    = " error: CMP buffer2 is a string"
    em3    =f" error: CMP operator {hex(op)} is invalid"
    
    tb1 = chk_target_buffer(buff1)
    tb2 = chk_target_buffer(buff2)
    
    if isinstance(buff[tb1], int): 0
    else: exit(em1)
    
    if isinstance(buff[tb2], int): 0
    else: exit(em2)
    
    if op <= 0x05: 0
    else: exit(em3)
    
    CMP_status = do_operator(buff1, buff2, op)

def JMP(address):   # 0x0C, 1 arg
    """
    address: <hex>
    desc: jumps PC to address index in code list
    """
    global PC
    PC = address

def JC(address):    # 0x0D, 1 arg
    """
    address: <hex>
    desc: jumps PC to address index in code list IF the CMP_status is true
    """
    global PC, CMP_status
    
    if CMP_status == True: PC = address
    else: PC += 2 #else skip JC and address argument

def JSR(address):   # 0x0E, 1 arg
    """
    address: <hex>
    desc: jumps PC to address index in code list
    then runs a code until it hits instruction 0x0F which is RTS
    then returns PC back to line where last JSR is called
    """
    global PC, last_JSR
    
    last_JSR.append(PC+2)
    PC = address

def RTS():      # 0x0F
    global PC, last_JSR
    em = " error: RTS is called with no previous JSR call"
    
    if last_JSR:
        new_PC = last_JSR.pop()
        if debug_mode == 0x01: print(f"debug: RTS back to where JSR was last called at PC={hex(new_PC)}")
        PC = new_PC
    else:
        exit(em)

def ADDS():     # 0x10
    """
    desc: joins string of buffer B into buffer A
    """
    em = " error: ADDS cannot add values, it must be strings"
    
    if isinstance(buff["A"], str) and isinstance(buff["B"], str): buff["A"] += buff["B"]
    else: exit(em)

def OUTH(_buff):  # 0x11, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: outputs hex value of the buffer
    """
    em = " error: cannot output hex buffer because it's a string"
    tb = chk_target_buffer(_buff)
    
    if isinstance(buff[tb], int): print(hex(buff[tb]))
    else: exit(em)

def SWAP(_2buff, _2tb): # 0x12, 1 arg
    """
    _2buff (
        0x00: buffer A
        0x01: buffer B
    )
    _2tb (
        0x00: buffer X
        0x01: buffer Y
    )
    desc: swaps buffer A or B with buffer X or Y
    """
    em1 = " error: SWAP invalid target buffer #1, must be A or B"
    em2 = " error: SWAP invalid target buffer #2, must be X or Y"
    tb  = "."
    
    if   _2tb == 0x00: temp_buff = buff["X"]; tb = "X"
    elif _2tb == 0x01: temp_buff = buff["Y"]; tb = "Y"
    else: exit(em2)
    
    if   _2buff == 0x00: buff[tb] = buff["A"]; buff["A"] = temp_buff
    elif _2buff == 0x01: buff[tb] = buff["B"]; buff["B"] = temp_buff
    else: exit(em1)

def CLC():  # 0x13
    """
    desc: clears all buffers
    """
    buff["A"] = 0x00
    buff["B"] = 0x00
    buff["X"] = 0x00
    buff["Y"] = 0x00

def AND():  # 0x14
    """
    desc: performs AND operation on buffer A and B
        then stores it on buffer X
    """
    result = 0x00
    em = " error: cannot perform AND operation on strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int): 0
    else: exit(em)
    
    result    = buff["A"] & buff["B"]
    buff["X"] = result

def OR():   # 0x15
    """
    desc: performs OR operation on buffer A and B
        then stores it on buffer X
    """
    result = 0x00
    em = " error: cannot perform OR operation on strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int): 0
    else: exit(em)
    
    result    = buff["A"] | buff["B"]
    buff["X"] = result

def XOR():  # 0x16
    """
    desc: performs XOR operation on buffer A and B
        then stores it on buffer X
    """
    result = 0x00
    em = " error: cannot perform XOR operation on strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int): 0
    else: exit(em)
    
    result    = buff["A"] ^ buff["B"]
    buff["X"] = result

def NOT():  # 0x17
    """
    desc: performs NOT operation on buffer A
        then stores it on buffer X
    """
    result = 0x00
    em = " error: cannot perform NOT operation on string, it must be value"
    
    if isinstance(buff["A"], int): 0
    else: exit(em)
    
    result    = ~ buff["A"]
    buff["X"] = result

def SHL(_buff):  # 0x18, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: bit-shifts a buffer to the left
    """
    tb = chk_target_buffer(_buff)
    em2 = " error: SHL cannot bit-shift a string, it must be value"
    
    if isinstance(buff[tb], int): 0
    else: exit(em2)
    
    buff[tb] = buff[tb] << 1
    buff[tb] = val_8bit(buff[tb])

def SHR(_buff):  # 0x19, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: bit-shifts a buffer to the right
    """
    tb = chk_target_buffer(_buff)
    em = " error: SHR cannot bit-shift a string, it must be value"
    
    if isinstance(buff[tb], int): 0
    else: exit(em)
    
    buff[tb] = buff[tb] >> 1
    buff[tb] = val_8bit(buff[tb])

def OUTB(_buff): # 0x1A, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: outputs buffer in binary code
    """
    tb = chk_target_buffer(_buff)
    em = " error: cannot output buffer in binary, it must be value"
    
    if isinstance(buff[tb], int): 0
    else: exit(em)
    
    bin_str = bin(buff[tb])[2:].zfill(8)
    print(bin_str)

def IN(_buff):   # 0x1B, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: takes input of user and puts it in buffer
    """
    tb = chk_target_buffer(_buff)
    
    #try to store it as hex value, otherwise store it as string
    buff[tb] = tryhex(input("input: "))

def WAIT(_buff): # 0x1C, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
        0x03: buffer Y
    )
    desc: pauses CPU for <buffer> seconds
    """
    tb = chk_target_buffer(_buff)
    em = " error: target buffer is not a value, cannot PAUSE"
    
    if isinstance(buff[tb], int):
        if debug_mode == 0x01: f"debug: pausing CPU for {buff[tb]} seconds"
        time.sleep(buff[tb])
    else: exit(em)

def RAND():     # 0x1D
    """
    min: buffer A
    max: buffer B
    desc: takes min and max range and then rolls random value
        then puts it in buffer X
    """
    _min = buff["A"]
    _max = buff["B"]
    _out = buff["X"]
    em  = " error: min or max is string, must be value"
    em2 = " error: max is less than min"
    em3 = " error: min and max both have same value"
    
    if isinstance(_min, int) and isinstance(_max, int): 0
    else: exit(em)
    
    if   _max < _min:  exit(em2)
    elif _max == _min: exit(em3)
    else:
        _out      = random.randint(_min, _max)
        buff["X"] = _out

def BEEP(loc, freq, dur): # 0x1E, 3 args
    """
    loc (
        0x00: rodata
        0x01: bss
    )
    freq: <address>
    dur:  <address>
    desc: plays a beep sound for <duration> miliseconds at <frequency> Hz
    """
    em = " error: min or max is a string, not value"
    
    chk_status = chk_address(loc, freq)
    chk()
    chk_status = chk_address(loc, dur)
    chk()
    
    freq_ = get_address_data(loc, freq)
    dur_  = get_address_data(loc, dur)
    
    if isinstance(freq_, int) and isinstance(dur_, int): 0
    else: exit(em)
    
    if debug_mode == 0x01:
        print(f"debug: BEEP played, freq: {freq_}Hz, dur: {dur_}ms")
    
    beep(freq_, dur_)

def HLT():      # 0x1F
    """
    desc: halt CPU
    """
    exit()

def LDY(loc, address):  # 0x20, 2 args
    """
    loc: (
        0x00: rodata
        0x01: bss
    )
    address: <hex>
    desc: load
    """
    
    #check if that address points to valid variable
    chk_status = chk_address(loc, address)
    chk()
    
    #then load that data to buffer Y
    buff["Y"] = get_address_data(loc, address)

def STY(address):       # 0x21, 1 arg
    """
    address: <hex>
    desc: store
    """
    size_address     = bss[address]["size"]
    data_address     = bss[address]["data"]
    len_data_address = trylen(buff["Y"])
    em = f" error: cannot fit string (size: {len_data_address}) inside bss {address} (size: {size_address})"
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #check for string overflow
    if isinstance(buff["Y"], str) and isinstance(data_address, str):
        if len_data_address <= size_address: 0
        else: exit(em)
    
    #store buffer Y into that address data
    set_address_data(buff["Y"], address)

def PNE():  # 0x22
    global pen_active
    pen_active = True

def PTO():  # 0x23
    global pen_active
    em = " PPU error: pen is not active yet"
    
    if pen_active:
        em2 = " PPU error: buffer X or Y is not value"
        
        if isinstance(buff["X"], int) and isinstance(buff["Y"], int): 0
        else: exit(em)
        
        ppu.move_pen(buff["X"], buff["Y"])
    else: exit(em)

def PDW():  # 0x24
    global pen_active
    em = " PPU error: pen is not active yet"
    
    if pen_active:
        ppu.pen_down = 0x1
    else: exit(em)

def PUP():  # 0x25
    global pen_active
    em = " PPU error: pen is not active yet"
    
    if pen_active:
        ppu.pen_down = 0x0
    else: exit(em)

def PCO(_buff):  # 0x26
    global pen_active
    em = " PPU error: pen is not active yet"
    
    if pen_active:
        em2 = " PPU error: target buffer is not value"
        tb = chk_target_buffer(_buff)
        
        if isinstance(buff[tb], int): 0
        else: exit(em2)
        
        ppu.set_color(buff[tb])
    else: exit(em)

def PDO():  # 0x27
    global pen_active
    pen_active = False
    ppu.pen_down = 0x0
    ppu.move_pen(0x00, 0x00)

def USC():  # 0x28
    global pen_active
    em = " PPU error: attempted to update frame while pen is active"
    
    if not pen_active: ppu.update_frame()
    else: exit(em)

def CLS():  # 0x29
    ppu.clear_screen()

#check:
## it makes sure you setted up rodata and bss correctly
def check():
    global rodata, bss, rodata_size, bss_size
    errors = 0
    
    ## rodata
    for i in range(len(rodata)):
        ap      = rodata[i]
        ap_addr = ap["addr"]
        ap_size = ap["size"]
        ap_data = ap["data"]
        
        if ap_size == 0x0: #size check
            print(f" rodata error: size of address {hex(ap_addr)} is 0x0")
            errors += 1
        
        if ap_addr > rodata_size: #bounds check
            new_rodata_size = rodata_size + abs(rodata_size-ap_addr)
            print(f" rodata error: address pointer {hex(ap_addr)} is out of bounds of rodata_size {hex(rodata_size)}")
            print(f"|SUGGESTED FIX: expand rodata_size from {hex(rodata_size)} to {hex(new_rodata_size)}")
            errors += 1
        
        new_ap = (ap_addr + ap_size) - 1
        
        if (i+1) in rodata: #check first if the next variable index exists first
            next_ap = rodata[i+1]
            if new_ap >= next_ap["addr"]: #if theres data on new ap then it's overlapping
                print(f" rodata error: data in address {hex(ap_addr)} is overlapping next address, size: {hex(ap_size)}")
                print(f"|SUGGESTED FIX: shift next address pointer until the data on current address pointer fits")
                errors += 1
            
        #check if the variable index's size match (or is bigger then) actual size of variable index's data
        actual_ap_size = trylen(ap_data)
        valid_ap_size = ap_size >= actual_ap_size
        if not valid_ap_size:
            print(f" rodata error: size in address {hex(ap_addr)} doesn't match actual size of data")
            print(f"|SUGGESTED FIX: change size of rodata address {hex(ap_addr)} to {hex(actual_ap_size)}")
            errors += 1
        
        #check if the variable is within 8bit
        if isinstance(ap_data, int):
            if ap_data <= 0xFF: 0
            else:
                print(f" rodata error: value in address {hex(ap_addr)} must be 8-bit")
                errors += 1
            
            #warning for unused occupied space
            if ap_size > 0x1:
                print(f" rodata warning: size of value address {hex(ap_addr)} has unused occupied space that is {hex(ap_size-1)} byte(s) large")
    
    ## bss
    for i in range(len(bss)):
        ap      = bss[i]
        ap_addr = ap["addr"]
        ap_size = ap["size"]
        ap_data = ap["data"]
        
        if ap_size == 0x0: #size check
            print(f" bss error: size of address {hex(ap_addr)} is 0x0")
            errors += 1
        
        if ap_addr > bss_size: #bounds check
            new_bss_size = bss_size + abs(bss_size-ap_addr)
            print(f" bss error: address pointer {hex(ap_addr)} is out of bounds of bss_size {hex(bss_size)}")
            print(f"|SUGGESTED FIX: expand bss_size from {hex(bss_size)} to {hex(new_bss_size)}")
            errors += 1
        
        new_ap  = (ap_addr + ap_size) - 1
        
        if (i+1) in bss: #check first if the next variable index exists first
            next_ap = bss[i+1]
            if new_ap >= next_ap["addr"]: #if theres data on new ap then it's overlapping
                print(f" bss error: data in address {hex(ap_addr)} is overlapping next address, size: {hex(ap_size)}")
                print(f"|SUGGESTED FIX: shift next address pointer until the data on current address pointer fits")
                errors += 1
        
        #check if the variable index's size match (or is bigger then) actual size of variable index's data
        actual_ap_size = trylen(ap_data)
        valid_ap_size = ap_size >= actual_ap_size
        if not valid_ap_size:
            print(f" bss error: size in address {hex(ap_addr)} doesn't match actual size of data")
            print(f"|SUGGESTED FIX: change size of bss address {hex(ap_addr)} to {hex(actual_ap_size)}")
            errors += 1
        
        #check if the variable is within 8bit
        if isinstance(ap_data, int):
            if ap_data <= 0xFF: 0
            else:
                print(f" bss error: value in address {hex(ap_addr)} must be 8-bit")
                errors += 1
            
            #warning for unused occupied space
            if ap_size > 0x1:
                print(f" bss warning: size of value address {hex(ap_addr)} has unused occupied space that is {hex(ap_size-1)} byte(s) large")
    
    ## check if there are errors:
    if errors > 0:
        print(f"\n{errors} error(s) are present")
        return False
    else:
        return True

chk_status = check()
chk()

#instruction list for debug message "ran instruction"
i_names = {
    0x00: "LDA",
    0x01: "LDB",
    0x02: "LDX",
    0x03: "STA",
    0x04: "STB",
    0x05: "STX",
    0x06: "INC",
    0x07: "DEC",
    0x08: "ADD",
    0x09: "SUB",
    0x0A: "OUT",
    0x0B: "CMP",
    0x0C: "JMP",
    0x0D: "JC",
    0x0E: "JSR",
    0x0F: "RTS",
    0x10: "ADDS",
    0x11: "OUTH",
    0x12: "SWAP",
    0x13: "CLC",
    0x14: "AND",
    0x15: "OR",
    0x16: "XOR",
    0x17: "NOT",
    0x18: "SHL",
    0x19: "SHR",
    0x1A: "OUTB",
    0x1B: "IN",
    0x1C: "WAIT",
    0x1D: "RAND",
    0x1E: "BEEP",
    0x1F: "HLT",
    0x20: "LDY",
    0x21: "STY",
    0x22: "PNE",
    0x23: "PTO",
    0x24: "PDW",
    0x25: "PUP",
    0x26: "PCO",
    0x27: "PDO",
    0x28: "USC",
    0x29: "CLS",
}

def get_i_name(i):
    return i_names.get(i, "unknown")

while PC < len(code):
    i = code[PC]
    
    if debug_mode == 0x01:
        print(f"debug: ran instruction {hex(i)} ({get_i_name(i)}) at PC={hex(PC)}")
    
    if i == 0x00:   LDA(code[PC+1], code[PC+2]); PC += 3
    elif i == 0x01: LDB(code[PC+1], code[PC+2]); PC += 3
    elif i == 0x02: LDX(code[PC+1], code[PC+2]); PC += 3
    elif i == 0x03: STA(code[PC+1]); PC += 2
    elif i == 0x04: STB(code[PC+1]); PC += 2
    elif i == 0x05: STX(code[PC+1]); PC += 2
    elif i == 0x06: INC(code[PC+1]); PC += 2
    elif i == 0x07: DEC(code[PC+1]); PC += 2
    elif i == 0x08: ADD(); PC += 1
    elif i == 0x09: SUB(); PC += 1
    elif i == 0x0A: OUT(code[PC+1]); PC += 2
    elif i == 0x0B: CMP(code[PC+1], code[PC+2], code[PC+3]); PC += 4
    elif i == 0x0C:
        if debug_mode == 0x01: print(f"debug: JMP to PC={hex(code[PC+1])}")
        JMP(code[PC+1])
    elif i == 0x0D:
        if debug_mode == 0x01 and CMP_status == True: print(f"debug: JC to PC={hex(code[PC+1])}")
        JC(code[PC+1])
    elif i == 0x0E:
        if debug_mode == 0x01: print(f"debug: JSR to PC={hex(code[PC+1])}")
        JSR(code[PC+1])
    elif i == 0x0F: RTS()
    elif i == 0x10: ADDS(); PC += 1
    elif i == 0x11: OUTH(code[PC+1]); PC += 2
    elif i == 0x12: SWAP(code[PC+1]); PC += 2
    elif i == 0x13: CLC(); PC += 1
    elif i == 0x14: AND(); PC += 1
    elif i == 0x15: OR();  PC += 1
    elif i == 0x16: XOR(); PC += 1
    elif i == 0x17: NOT(); PC += 1
    elif i == 0x18: SHL(code[PC+1]); PC += 2
    elif i == 0x19: SHR(code[PC+1]); PC += 2
    elif i == 0x1A: OUTB(code[PC+1]); PC += 2
    elif i == 0x1B: IN(code[PC+1]); PC += 2
    elif i == 0x1C: WAIT(code[PC+1]); PC += 2
    elif i == 0x1D: RAND(); PC += 1
    elif i == 0x1E: BEEP(code[PC+1], code[PC+2], code[PC+3]); PC += 4
    elif i == 0x1F: HLT(); PC += 1
    elif i == 0x20: LDY(code[PC+1], code[PC+2]); PC += 3
    elif i == 0x21: STY(code[PC+1]); PC += 2
    elif i == 0x22: PNE(); PC += 1
    elif i == 0x23: PTO(); PC += 1
    elif i == 0x24: PDW(); PC += 1
    elif i == 0x25: PUP(); PC += 1
    elif i == 0x26: PCO(code[PC+1]); PC += 2
    elif i == 0x27: PDO(); PC += 1
    elif i == 0x28: USC(); PC += 1
    elif i == 0x29: CLS(); PC += 1
    else:
        print(f" fatal error: invalid instruction {hex(i)}")
        exit()
    
    chk_buffers_size()
    
    A = buff["A"]
    B = buff["B"]
    X = buff["X"]
    Y = buff["Y"]
    
    if debug_mode == 0x1:
        #for debug, print all buffers and more
        print(f"debug: compare status {hex(CMP_status)}")
        print(f"debug: pen active {hex(pen_active)}")
        print(f"debug: A  = {tryhex(A)}" )
        print(f"debug: B  = {tryhex(B)}" )
        print(f"debug: X  = {tryhex(X)}" )
        print(f"debug: Y  = {tryhex(Y)}" )
        print(f"debug: PC = {hex(PC)}"   )

print(" end of execution")
while ppu.running: ppu.update_frame()
exit()
