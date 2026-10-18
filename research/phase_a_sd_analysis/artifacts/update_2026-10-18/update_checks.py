"""Raw checks for the update-path pass, 2026-10-18. Run from firmware/."""
import mmap, re, struct, collections, hashlib, subprocess
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
IMG = 'firmware/image/sdcard.work.img'
FH = open(IMG, 'rb')
m = mmap.mmap(FH.fileno(), 0, access=mmap.ACCESS_READ)
app = open('firmware/bin/ZK-INKJET-NANO-APP.bin', 'rb').read()
boot = open('firmware/bin/ZK-INKJET-NANO-BOOT.bin', 'rb').read()
P = print
P('Checks for the update-path pass, 2026-10-18 (generated, raw output).')
P('card image %s, %#x bytes; APP VA = file + 0x58000 (CL-BOOT-REC-113)' % (IMG, len(m)))

P('\n1. NANO APP update code (capstone over firmware/bin/ZK-INKJET-NANO-APP.bin)')
def dis(data, foff, n, va_off):
    for i in md.disasm(data[foff:foff + 4 * n], foff + va_off):
        P('   %06x: %s %s' % (i.address, i.mnemonic, i.op_str))
for va, n in [(0xC087C, 28), (0xC4D8C, 12), (0xC4DD0, 16), (0xC4EC8, 14), (0xC5080, 34), (0xC5168, 8), (0xC5248, 4), (0xC52A0, 6), (0x8A500, 20), (0x8A730, 10), (0xA83A8, 16), (0xA8404, 6), (0xB3120, 8), (0xB31CC, 9)]:
    P('  -- VA %#x' % va); dis(app, va - 0x58000, n, 0x58000)
P('  pool VA 0x8A758 = %#x (TMR_BA; +0x1C is WTCR)' % struct.unpack_from('<I', app, 0x8A758 - 0x58000)[0])
tpl = app[0x6CFA8:0x6CFA8 + 32]
P('  template VA 0xC4FA8 (file+0x6CFA8):', [hex(w) for w in struct.unpack('<8I', tpl)])
for va in (0xC08F0, 0xC08FC, 0xC091C, 0xC4FE0, 0xC4FFC, 0xC5018, 0xC5034, 0xC5048, 0xC5064):
    P('  string VA %#x: %r' % (va, re.match(rb'[\x20-\x7e]+', app[va - 0x58000:va - 0x58000 + 48]).group().decode()))

P('\n2. Boot header and BOOT.bin on the card')
P('  card 0x200..0x220 == template:', m[0x200:0x220] == tpl)
P('  card 0x220.. == BOOT.bin (%#x bytes):' % len(boot), m[0x220:0x220 + len(boot)] == boot)
P('  card 0x33E0..0x3400 (sector tail after BOOT):', m[0x33E0:0x3400].hex())

P('\n3. All copies of the 32-byte template on the card')
hits = []; i = m.find(tpl)
while i != -1: hits.append(i); i = m.find(tpl, i + 1)
P('  full template:', [hex(h) for h in hits])
mk = struct.pack('<I', 0x57425AA5); h3 = []; i = m.find(mk)
while i != -1: h3.append(i); i = m.find(mk, i + 1)
P('  marker word 0x57425AA5 alone:', [hex(h) for h in h3])

P('\n4. Firmware builds on the card')
imgs = [('NANO', 0x3000000, len(app)), ('ZK-INKJET', 0x100000, 0x2DCBAE), ('TIJSPS', 0x2400000, 0x32EB9F), ('CUTE', 0x3C00000, 0x400000)]
datere = rb'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ 0-9][0-9] 20[0-9][0-9]\x00[^\x00]*\x00*([0-2][0-9]:[0-5][0-9]:[0-5][0-9])'
P('  card 0x3000000.. == APP.bin:', m[0x3000000:0x3000000 + len(app)] == app)
for nm, b, L in imgs:
    d = bytes(m[b:b + L])
    st = [(hex(x.start()), x.group(0)[:11].decode(), x.group(2).decode()) for x in re.finditer(datere, d)]
    P('  %-9s card %#x word0 %#x stamps %s' % (nm, b, struct.unpack_from('<I', d)[0], st))
    for s in re.finditer(rb'3:/[A-Za-z0-9_\-/.]{3,48}\.(bin|spiflash)\x00', d):
        pass

def bl_sites(d, target):
    out = []
    for off in range(0, len(d) - 3, 4):
        ins = struct.unpack_from('<I', d, off)[0]
        if (ins & 0x0F000000) == 0x0B000000 and (ins >> 28) != 0xF:
            imm = ins & 0xFFFFFF; imm = imm - (1 << 24) if imm & 0x800000 else imm
            if off + 8 + imm * 4 == target: out.append(off)
    return out
def ctx(d, site):
    r0 = r1 = r2 = None
    for i in md.disasm(d[site - 0x40:site + 4], site - 0x40):
        if i.mnemonic in ('mov', 'add', 'sub', 'ldr') and i.op_str.startswith('r1, '): r1 = i.op_str[4:]
        if i.mnemonic in ('mov', 'add', 'sub', 'ldr') and i.op_str.startswith('r0, '): r0 = i.op_str[4:]
        if i.mnemonic == 'add' and i.op_str.startswith('r2, pc, #'):
            a = i.address + 8 + int(i.op_str.split('#')[1], 16)
            s = re.match(rb'[\x20-\x7e]+', d[a:a + 60]); r2 = s.group().decode() if s else hex(a)
    return r0, r1, r2
P('\n5. Calls of each build\'s update_flash_file_to_raw (file offsets; r0/r1 = last mov/add/sub/ldr into them within 16 instructions, heuristic -- r1 is the raw card offset)')
for nm, b, L, fn in [('NANO', 0x3000000, len(app), 0xC4CF8 - 0x58000), ('ZK-INKJET', 0x100000, 0x2DCBAE, 0x79A94), ('TIJSPS', 0x2400000, 0x32EB9F, 0x7A730), ('CUTE', 0x3C00000, 0x400000, 0x7BA38)]:
    d = bytes(m[b:b + L]); P('  ==', nm, 'function at file+%#x' % fn)
    for s in bl_sites(d, fn):
        r0, r1, r2 = ctx(d, s); P('     bl at file+%#x  r0=%s  r1=%s  file=%s' % (s, r0, r1, r2))

P('\n6. Set-A BOOT path of the ZK-INKJET build (image linked at 0, card 0x100000)')
zk = bytes(m[0x100000:0x100000 + 0x2DCBAE])
for a, n in [(0x79CC8, 34), (0x79F00, 12), (0x79F80, 20), (0x79FE8, 32), (0x7A104, 6), (0xAA568, 12), (0xAA438, 10), (0xAA4D0, 4)]:
    P('  -- %#x' % a)
    for i in md.disasm(zk[a:a + 4 * n], a):
        x = ''
        if i.mnemonic.startswith('ldr') and '[pc, #' in i.op_str:
            x = '   ; =%#x' % struct.unpack_from('<I', zk, i.address + 8 + int(i.op_str.split('#')[1].rstrip(']'), 16))[0]
        P('     %06x: %s %s%s' % (i.address, i.mnemonic, i.op_str, x))
P('  driver table 0xE5190:', [hex(x) for x in struct.unpack_from('<8I', zk, 0xE5190)])
for nm, a in [('A 0x190', 0xE8158), ('B 0x1D0', 0xE82E8)]:
    P('  header table %s at %#x:' % (nm, a), [hex(x) for x in struct.unpack_from('<16I', zk, a)])

P('\n7. Peripheral base words per build (aligned 32-bit words in [base, base+0x400))')
probes = [('N3290x UDC', 0xB1008000), ('N3290x SPIMS0', 0xB800C000), ('N3290x GPIO', 0xB8001000), ('N3290x RTC / other GPIO', 0xB8003000),
          ('SPI 0xB8006200', 0xB8006200), ('unlock 0xB00001FC', 0xB00001FC), ('EHCI 0xB0005000', 0xB0005000), ('OHCI 0xB0007000', 0xB0007000), ('USBD 0xB0006000', 0xB0006000)]
for nm, b, L in imgs:
    d = bytes(m[b:b + L]); w = collections.Counter(struct.unpack_from('<%dI' % (len(d) // 4), d))
    P('  %-9s' % nm, ', '.join('%s=%d' % (pn, sum(c for x, c in w.items() if pv <= x < pv + 0x400)) for pn, pv in probes))

P('\n8. Tail after APP.bin at card 0x03000000 (update writes whole sectors from a reused 0x1000 buffer)')
L = len(app); tail = m[0x3000000 + L:0x3000000 + ((L + 0x1FF) & ~0x1FF)]
prev = app[(L & ~0xFFF) - 0x1000 + (L & 0xFFF):(L & ~0xFFF) - 0x1000 + (((L + 0x1FF) & ~0x1FF) & 0xFFF)]
P('  card %#x..%#x (%d bytes) == APP bytes %#x..%#x: %s' % (0x3000000 + L, 0x3000000 + ((L + 0x1FF) & ~0x1FF), len(tail), (L & ~0xFFF) - 0x1000 + (L & 0xFFF), (L & ~0xFFF) - 0x1000 + (((L + 0x1FF) & ~0x1FF) & 0xFFF), tail == prev))

P('\n9. Volume USER (MBR at card 0x24000000, FAT16 at 0x24007E00) and MINI')
P('  MBR 0x24000000 entry 1:', m[0x240001BE:0x240001CE].hex(), 'sig', m[0x240001FE:0x24000200].hex())
o = 0x24007E00 // 512
P(subprocess.run(['fls', '-r', '-p', '-l', '-o', str(o), IMG], capture_output=True, text=True).stdout)
for ino in (10, 13, 16):
    data = subprocess.run(['icat', '-r', '-o', str(o), IMG, str(ino)], capture_output=True).stdout
    P('  inode %d: %d bytes sha256 %s' % (ino, len(data), hashlib.sha256(data).hexdigest()))
P('  BOOT.bin sha256', hashlib.sha256(boot).hexdigest(), '/ APP.bin sha256', hashlib.sha256(app).hexdigest())
P(subprocess.run(['fls', '-r', '-p', '-l', '-o', str(0x2A61BE00 // 512), IMG], capture_output=True, text=True).stdout)
