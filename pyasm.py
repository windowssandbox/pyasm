import sys
import random

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
    0x0: {
        "addr": 0x0000,
        "data": 0x00,
        "size": 0x1
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
## <opcode>, <its arguments>, # (instruction in text format)
## (put multiple indexes in one line)
code = [
    ## main: 0x00
        
]

#buffers
buff = { 
    "A": 0x00,
    "B": 0x00,
    "X": 0x00,
}

#check for main
def exit(msg=""):
    if not msg == "": print(msg)
    input("press enter to exit")
    sys.exit()

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
    
    Fer = " fatal error:"
    Aem = f" {Fer} buffer A overflowed by {hex(As-buff_size)} bytes"
    Bem = f" {Fer} buffer B overflowed by {hex(Bs-buff_size)} bytes"
    Xem = f" {Fer} buffer X overflowed by {hex(Xs-buff_size)} bytes"
    sf  = f"|SUGGESTED FIX: expand buff_size to {hex(new_buff_size)} bytes"
    
    if As <= buff_size: 0
    else: print(Aem); new_buff_size = buff_size+As; print(sf); exit()
    if Bs <= buff_size: 0
    else: print(Bem); new_buff_size = buff_size+Bs; print(sf); exit()
    if Xs <= buff_size: 0
    else: print(Xem); new_buff_size = buff_size+Xs; print(sf); exit()

def chk_target_buffer(_buff):
    tb = "."
    em = " error: invalid target buffer"
    
    if   _buff == 0x00: tb = "A"
    elif _buff == 0x01: tb = "B"
    elif _buff == 0x02: tb = "X"
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
    if buff1 == 0x00 and buff2 == 0x00:
        if op == 0x00: return buff["A"] == buff["A"]
        if op == 0x01: return buff["A"] != buff["A"]
        if op == 0x02: return buff["A"] >  buff["A"]
        if op == 0x03: return buff["A"] <  buff["A"]
        if op == 0x04: return buff["A"] >= buff["A"]
        if op == 0x05: return buff["A"] <= buff["A"]
    elif buff1 == 0x01 and buff2 == 0x00:
        if op == 0x00: return buff["B"] == buff["A"]
        if op == 0x01: return buff["B"] != buff["A"]
        if op == 0x02: return buff["B"] >  buff["A"]
        if op == 0x03: return buff["B"] <  buff["A"]
        if op == 0x04: return buff["B"] >= buff["A"]
        if op == 0x05: return buff["B"] <= buff["A"]
    elif buff1 == 0x02 and buff2 == 0x00:
        if op == 0x00: return buff["X"] == buff["A"]
        if op == 0x01: return buff["X"] != buff["A"]
        if op == 0x02: return buff["X"] >  buff["A"]
        if op == 0x03: return buff["X"] <  buff["A"]
        if op == 0x04: return buff["X"] >= buff["A"]
        if op == 0x05: return buff["X"] <= buff["A"]
    
    elif buff1 == 0x00 and buff2 == 0x01:
        if op == 0x00: return buff["A"] == buff["B"]
        if op == 0x01: return buff["A"] != buff["B"]
        if op == 0x02: return buff["A"] >  buff["B"]
        if op == 0x03: return buff["A"] <  buff["B"]
        if op == 0x04: return buff["A"] >= buff["B"]
        if op == 0x05: return buff["A"] <= buff["B"]
    elif buff1 == 0x01 and buff2 == 0x01:
        if op == 0x00: return buff["B"] == buff["B"]
        if op == 0x01: return buff["B"] != buff["B"]
        if op == 0x02: return buff["B"] >  buff["B"]
        if op == 0x03: return buff["B"] <  buff["B"]
        if op == 0x04: return buff["B"] >= buff["B"]
        if op == 0x05: return buff["B"] <= buff["B"]
    elif buff1 == 0x02 and buff2 == 0x01:
        if op == 0x00: return buff["X"] == buff["B"]
        if op == 0x01: return buff["X"] != buff["B"]
        if op == 0x02: return buff["X"] >  buff["B"]
        if op == 0x03: return buff["X"] <  buff["B"]
        if op == 0x04: return buff["X"] >= buff["B"]
        if op == 0x05: return buff["X"] <= buff["B"]
    
    elif buff1 == 0x00 and buff2 == 0x02:
        if op == 0x00: return buff["A"] == buff["X"]
        if op == 0x01: return buff["A"] != buff["X"]
        if op == 0x02: return buff["A"] >  buff["X"]
        if op == 0x03: return buff["A"] <  buff["X"]
        if op == 0x04: return buff["A"] >= buff["X"]
        if op == 0x05: return buff["A"] <= buff["X"]
    elif buff1 == 0x01 and buff2 == 0x02:
        if op == 0x00: return buff["B"] == buff["X"]
        if op == 0x01: return buff["B"] != buff["X"]
        if op == 0x02: return buff["B"] >  buff["X"]
        if op == 0x03: return buff["B"] <  buff["X"]
        if op == 0x04: return buff["B"] >= buff["X"]
        if op == 0x05: return buff["B"] <= buff["X"]
    elif buff1 == 0x02 and buff2 == 0x02:
        if op == 0x00: return buff["X"] == buff["X"]
        if op == 0x01: return buff["X"] != buff["X"]
        if op == 0x02: return buff["X"] >  buff["X"]
        if op == 0x03: return buff["X"] <  buff["X"]
        if op == 0x04: return buff["X"] >= buff["X"]
        if op == 0x05: return buff["X"] <= buff["X"]

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
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #store buffer A into that address data
    set_address_data(buff["A"], address)

def STB(address):       # 0x04, 1 arg
    """
    address: <hex>
    desc: store
    """
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #store buffer B into that address data
    set_address_data(buff["B"], address)

def STX(address):       # 0x05, 1 arg
    """
    address: <hex>
    desc: store
    """
    
    #check if address points to valid one in bss
    chk_status = chk_address(0x1, address)
    chk()
    
    #store buffer X into that address data
    set_address_data(buff["X"], address)

def INC(_buff): # 0x06, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
    )
    desc: increment
    """
    em  = " error: cannot increment a string"
    em2 = " error: target buffer is invalid"
    
    if _buff == 0x00:
        if isinstance(buff["A"], int): buff["A"] += 1
        else: print(em); exit()
    elif _buff == 0x01:
        if isinstance(buff["B"], int): buff["B"] += 1
        else: print(em); exit()
    elif _buff == 0x02:
        if isinstance(buff["X"], int): buff["X"] += 1
        else: print(em); exit()
    else:
        print(em2); exit()

def DEC(_buff): # 0x07, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
    )
    desc: decrement
    """
    em  = " error: cannot decrement a string"
    em2 = " error: target buffer is invalid"
    
    if _buff == 0x00:
        if isinstance(buff["A"], int): buff["A"] -= 1
        else: print(em); exit()
    elif _buff == 0x01:
        if isinstance(buff["B"], int): buff["B"] -= 1
        else: print(em); exit()
    elif _buff == 0x02:
        if isinstance(buff["X"], int): buff["X"] -= 1
        else: print(em); exit()
    else:
        print(em2); exit()

def ADD():      # 0x08
    """
    desc: adds value of buffer B into buffer A
    """
    em = " error: ADD cannot add strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int): buff["A"] += buff["B"]
    else: print(em); exit()

def SUB():      # 0x09
    """
    desc: subtracts value of buffer B from buffer A
    """
    em = " error: cannot subtract strings, it must be values"
    
    if isinstance(buff["A"], int) and isinstance(buff["B"], int): buff["A"] -= buff["B"]
    else: print(em); exit()

def OUT(_buff): # 0x0A, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
    )
    desc: outputs data of the buffer
    """
    em = " error: target buffer is invalid"
    
    if   _buff == 0x00: print(buff["A"])
    elif _buff == 0x01: print(buff["B"])
    elif _buff == 0x02: print(buff["X"])
    else: print(em); exit()

def CMP(buff1, buff2, op): # 0x0B, 3 args
    """
    buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
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
    em1    = " error: CMP buffer1 is a string, or target buffer1 is invalid"
    em2    = " error: CMP buffer2 is a string, or target buffer2 is invalid"
    em3    =f" error: CMP operator {hex(op)} is invalid"
    
    if   buff1 == 0x00 and isinstance(buff["A"], int): 0
    elif buff1 == 0x01 and isinstance(buff["B"], int): 0
    elif buff1 == 0x02 and isinstance(buff["X"], int): 0
    else: print(em1); exit()
    
    if   buff2 == 0x00 and isinstance(buff["A"], int): 0
    elif buff2 == 0x01 and isinstance(buff["B"], int): 0
    elif buff2 == 0x02 and isinstance(buff["X"], int): 0
    else: print(em2); exit()
    
    if   op == 0x00: 0
    elif op == 0x01: 0
    elif op == 0x02: 0
    elif op == 0x03: 0
    elif op == 0x04: 0
    elif op == 0x05: 0
    else: print(em3); exit()
    
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
        PC = last_JSR.pop()
    else:
        print(em); exit()

def ADDS():     # 0x10
    """
    desc: joins string of buffer B into buffer A
    """
    em = " error: ADDS cannot add values, it must be strings"
    
    if isinstance(buff["A"], str) and isinstance(buff["B"], str): buff["A"] += buff["B"]
    else: print(em); exit()

def OUTH(_buff):  # 0x11, 1 arg
    """
    _buff (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
    )
    desc: outputs hex value of the buffer
    """
    em = " error: cannot output hex buffer because it's a string, or target buffer is invalid"
    
    if   _buff == 0x00 and isinstance(buff["A"], int): print(hex(buff["A"]))
    elif _buff == 0x01 and isinstance(buff["B"], int): print(hex(buff["B"]))
    elif _buff == 0x02 and isinstance(buff["X"], int): print(hex(buff["X"]))
    else: print(em); exit()

def SWAP(_2buff): # 0x12, 1 arg
    """
    _2buff (
        0x00: buffer A
        0x01: buffer B
    )
    desc: swaps buffer A or B with buffer X
    """
    em = " error: invalid target buffer"
    temp_buff = buff["X"]
    
    if   _2buff == 0x00: buff["X"] = buff["A"]; buff["A"] = temp_buff
    elif _2buff == 0x01: buff["X"] = buff["B"]; buff["B"] = temp_buff
    else: print(em); exit()

def CLC():  # 0x13
    """
    desc: clears all buffers
    """
    buff["A"] = 0x00
    buff["B"] = 0x00
    buff["X"] = 0x00

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
    )
    desc: bit-shifts a buffer to the left
    """
    tb = chk_target_buffer(_buff)
    em2 = " error: SHL cannot bit-shift a string, it must be value"
    
    if isinstance(buff[tb], int): 0
    else: exit(em2)
    
    buff[tb] = buff[tb] << 1

def SHR(_buff):  # 0x19, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
    )
    desc: bit-shifts a buffer to the right
    """
    tb = chk_target_buffer(_buff)
    em = " error: SHR cannot bit-shift a string, it must be value"
    
    if isinstance(buff[tb], int): 0
    else: exit(em)
    
    buff[tb] = buff[tb] >> 1

def OUTB(_buff): # 0x1A, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
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
    )
    desc: takes input of user and puts it in buffer
    """
    tb = chk_target_buffer(_buff)
    em = " error: invalid target buffer"
    
    #try to store it as hex value, otherwise store it as string
    buff[tb] = tryhex(input("input: "))

def PAUSE(_buff): # 0x1C, 1 arg
    """
    buffer (
        0x00: buffer A
        0x01: buffer B
        0x02: buffer X
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
    
    ## bss
    for i in range(len(bss)):
        ap      = bss[i]
        ap_addr = ap["addr"]
        ap_size = ap["size"]
        ap_data = ap["data"]
        
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
    
    ## check if there are errors:
    if errors > 0:
        print(f"\n{errors} error(s) are present")
        return False
    else:
        return True

chk_status = check()
chk()

prev_PC = 0x0000

while PC < len(code):
    prev_PC = PC
    i = code[PC]
    
    if debug_mode == 0x01:
        print(f"debug: ran instruction {hex(i)} at PC={hex(PC)}")
    
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
    elif i == 0x0F:
        if debug_mode == 0x01: print(f"debug: RTS back to where JSR was last called")
        RTS()
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
    elif i == 0x1C: PAUSE(code[PC+1]); PC += 2
    elif i == 0x1D: RAND(); PC += 1
    elif i == 0x1E: BEEP(code[PC+1], code[PC+2], code[PC+3]); PC += 4
    elif i == 0x1F: HLT(); PC += 1
    else:
        print(f" fatal error: invalid instruction {hex(i)}")
        exit()
    
    chk_buffers_size()
    
    A  = buff["A"]
    B  = buff["B"]
    X  = buff["X"]
    
    if debug_mode == 0x1:
        #for debug, print all buffers and more
        print(f"debug: compare status {hex(CMP_status)}")
        print(f"debug: A  = {tryhex(A)}" )
        print(f"debug: B  = {tryhex(B)}" )
        print(f"debug: X  = {tryhex(X)}" )
        print(f"debug: PC = {hex(PC)}"   )

print(" end of execution")
exit()
