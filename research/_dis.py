import sys, capstone

with open('firmware/bin/ZK-INKJET-NANO-APP.bin','rb') as f:
    data = f.read()

BASE = 0x200000

def dis(va, mode, n=12):
    off = va - BASE
    md = capstone.Cs(capstone.CS_ARCH_ARM, mode)
    chunk = data[off:off+ (n*4)]
    cnt=0
    for insn in md.disasm(chunk, va):
        print('  0x%08x: %-8s %s' % (insn.address, insn.mnemonic, insn.op_str))
        cnt+=1
        if cnt>=n: break

args = sys.argv[1:]
va = int(args[0],16)
mode = capstone.CS_MODE_THUMB if (len(args)>1 and args[1]=='t') else capstone.CS_MODE_ARM
n = int(args[2]) if len(args)>2 else 12
print("VA 0x%08x mode=%s" % (va, 'THUMB' if mode==capstone.CS_MODE_THUMB else 'ARM'))
dis(va, mode, n)
