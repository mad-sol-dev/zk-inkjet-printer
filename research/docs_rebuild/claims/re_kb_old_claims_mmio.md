# MMIO Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## MMIO Base Addresses

### ✅ Verified CL-RKO-MMIO-001: MMIO Global Control Registers (GCR_BA @ 0xB0000000)
**Claim:** Firmware extensively accesses GCR_BA @ 0xB0000000 for system and global control. 54 direct register accesses confirmed. Key registers include GPBFUN @ 0xB0000084 (Port B pin multiplexing) and clock/bus/gate control @ 0xB0000204. Registers manipulated with read-modify-write patterns for setting/clearing control bits.

**Evidence:**
- E-RKO-MMIO-001: Representative usage: Load GCR_BA (#0xb0000000), read clock control @ +0x204, set bit (#0x1000000), write back. Pattern: mov r4,#0xb0000000; ldr r0,[r4,#0x204]; orr r0,r0,#0x1000000; str r0,[r4,#0x204]
- E-RKO-MMIO-001: 54 direct accesses to GCR_BA identified in firmware via literal pool and scalar search
- E-RKO-MMIO-001: Memory map shows GCR_BA @ 0xB000_0000 - 0xB000_01FF for System and Global Control Registers

**Status:** ✅ Verified
**Cross-Reference:** None noted
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-MMIO-002: MMIO Doorbell/Parameter Block (0xB800C000)
**Claim:** Firmware uses doorbell/parameter interface @ 0xB800C000 for display-related commands. Register layout: +0x00 (command/status with bit 0 = busy), +0x10 (param1), +0x14 (param2), +0x18 (param3), +0x1C (param4). Pattern: poll busy bit, write 4 parameters, write command to trigger operation.

**Evidence:**
- E-RKO-MMIO-002: Doorbell usage pattern: ldr r12,[0x270188] loads base 0xB800C000, then polls status @ +0x0 (tst r10,#0x1; bne wait_loop), writes params to +0x10/14/18/1C, writes command to +0x0 to trigger
- E-RKO-MMIO-002: Literal @ 0x00270188 contains address 0xB800C000
- E-RKO-MMIO-002: N32903 peripheral addressing (doorbell register not in standard peripheral map, likely custom/undocumented)

**Status:** ✅ Verified
**Cross-Reference:** None noted
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-MMIO-003: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
**Claim:** Display controller @ 0xB100D000 used for hardware display updates with wait-for-ready pattern (poll bit 0 until clear, write color/coordinate data, set bit 0 to trigger). GPIO base @ 0xB8001000 (GP_BA) accessed indirectly with port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Per-port register offsets: OMD=+0x10, PUEN=+0x14, DOUT=+0x18, PIN=+0x1C.

**Evidence:**
- E-RKO-MMIO-003: Hardware display update routine uses literal @ 0x00230F34 (value 0xB100D000). Waits for bit 0 clear, writes display data, sets bit 0 to trigger update.
- E-RKO-MMIO-003: GPIO base 0xB8001000 accessed with indirect addressing pattern. Port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Register offsets per port: OMD=+0x10 (Output Mode), PUEN=+0x14 (Pull-Up Enable), DOUT=+0x18 (Data Output), PIN=+0x1C (Pin Input)
- E-RKO-MMIO-003: GPIO control register map shows GP_BA = 0xB8001000 with register layout matching firmware usage

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-MMIO-004: MMIO UART Controller (UA_BA @ 0xB8008000)
**Claim:** UART peripheral base is UA_BA @ 0xB800_8000–0xB800_8FFF per N3290x memory map. Datasheet section 6.22 documents two UART channels (UART0 high-speed with flow control, UART1 normal-speed). Firmware scalar searches in both ZK-INKJET-NANO-APP.bin and ZK-INKJET-NANO-BOOT.bin show no direct accesses to this base, implying UART is likely unused in these builds.

**Evidence:**
- E-RKO-MMIO-004: Memory map shows UA_BA @ 0xB800_8000 - 0xB800_8FFF for UART Control Registers
- E-RKO-MMIO-004: UART controller overview and dual-channel description (UART0 high-speed with CTS/RTS, UART1 normal speed)
- E-RKO-MMIO-004: Ghidra scalar search for 0xB8008000 returned 0 matches (no firmware register touches observed)
- E-RKO-MMIO-004: Bootloader image also has no scalar references to UA_BA

**Status:** ✅ Verified
**Cross-Reference:** None noted
**Next Tests:** None listed

---
