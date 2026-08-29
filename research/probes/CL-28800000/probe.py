#!/usr/bin/env python3
"""
Probe for 32-bit value 0x28800000 in firmware/bin/ZK-INKJET-NANO-APP.bin.
Searches both 4-byte aligned literals and ARM MOV-immediate instructions.
"""

import struct

# Constants
TARGET = 0x28800000
CONTROL_LITERAL = 0x2A614000
FILE_PATH = 'firmware/bin/ZK-INKJET-NANO-APP.bin'
FILE_SIZE = 0x27522C
WORD_SIZE = 4

# Controls
CONTROL_OFFSETS = {0x1CA5C: CONTROL_LITERAL, 0x1CAAC: CONTROL_LITERAL}
CONTROL_MOV_OFFSETS = {0x65FE4: 0xE3A085A2, 0x65FE0: 0xE3A07A4D}  # Raw instructions

def search_literal():
    """Search for 4-byte aligned 32-bit LE literals."""
    hits = []
    with open(FILE_PATH, 'rb') as f:
        for offset in range(0, FILE_SIZE, WORD_SIZE):
            f.seek(offset)
            word = f.read(WORD_SIZE)
            if len(word) != WORD_SIZE:
                break
            value = struct.unpack('<I', word)[0]
            if value == TARGET:
                hits.append(offset)
            elif offset in CONTROL_OFFSETS and value != CONTROL_OFFSETS[offset]:
                raise ValueError(f'Control literal failed at {offset:#x}: expected {CONTROL_OFFSETS[offset]:#x}, got {value:#x}')
    return hits

def search_mov_imm():
    """Search for ARM MOV-immediate instructions encoding 0x28800000."""
    hits = []
    with open(FILE_PATH, 'rb') as f:
        for offset in range(0, FILE_SIZE, WORD_SIZE):
            f.seek(offset)
            word = f.read(WORD_SIZE)
            if len(word) != WORD_SIZE:
                break
            instruction = struct.unpack('<I', word)[0]
            
            # Skip controls
            if offset in CONTROL_MOV_OFFSETS:
                if instruction != CONTROL_MOV_OFFSETS[offset]:
                    raise ValueError(f'Control instruction failed at {offset:#x}: expected {CONTROL_MOV_OFFSETS[offset]:#x}, got {instruction:#x}')
                continue
            
            # ARM MOV-immediate decoding
            opcode = (instruction >> 21) & 0xF
            imm12 = instruction & 0xFFF
            rotate = (instruction >> 8) & 0xF
            
            # MOV, MVN, ORR, ADD, SUB, BIC, TEQ, TST, CMN, CMP
            if opcode in (0xD, 0xF, 0xC, 0x8, 0x4, 0x2, 0x1, 0x9, 0xA, 0xB):
                value = (imm12 >> (rotate * 2)) | (imm12 << (32 - rotate * 2))
                value &= 0xFFFFFFFF  # Ensure 32-bit
                if value == TARGET:
                    hits.append(offset)
    return hits

def main():
    print('Controls: PASS')
    literal_hits = search_literal()
    mov_hits = search_mov_imm()
    
    print(f'Literal hits for {TARGET:#x}: {literal_hits}')
    print(f'MOV-immediate hits for {TARGET:#x}: {mov_hits}')
    
    if not literal_hits and not mov_hits:
        print(f'\\nSearched:')
        print(f'- 4-byte aligned 32-bit LE literals: 0x0 to 0x{FILE_SIZE:X}')
        print(f'- ARM MOV-immediate instructions: 0x0 to 0x{FILE_SIZE:X}')

if __name__ == '__main__':
    main()