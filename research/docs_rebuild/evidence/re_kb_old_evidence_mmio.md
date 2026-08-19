# MMIO Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## MMIO Base Addresses

### E-RKO-MMIO-001: MMIO Global Control Registers (GCR_BA @ 0xB0000000)
- **RE-KB ID:** finding-0004
- **Status:** verified
- **Type:** behavior
- **Summary:** Firmware extensively accesses GCR_BA @ 0xB0000000 for system and global control. 54 direct register accesses confirmed. Key registers include GPBFUN @ 0xB0000084 (Port B pin multiplexing) and clock/bus/gate control @ 0xB0000204. Registers manipulated with read-modify-write patterns for setting/clearing control bits.
- **Evidence:**
  - E1: Representative usage: Load GCR_BA (#0xb0000000), read clock control @ +0x204, set bit (#0x1000000), write back. Pattern: mov r4,#0xb0000000; ldr r0,[r4,#0x204]; orr r0,r0,#0x1000000; str r0,[r4,#0x204]; source_type=ghidra; function_address=0x6fc24; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: 54 direct accesses to GCR_BA identified in firmware via literal pool and scalar search; source_type=other [ghidra-v1]
  - E3: Memory map shows GCR_BA @ 0xB000_0000 - 0xB000_01FF for System and Global Control Registers; source_type=pdf; page=48 [ghidra-v1]
- **Tags:** mmio, gcr, system-control, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:13:42.090459Z
- **Updated:** 2025-12-02T03:05:06.692196Z

### E-RKO-MMIO-002: MMIO Doorbell/Parameter Block (0xB800C000)
- **RE-KB ID:** finding-0005
- **Status:** verified
- **Type:** behavior
- **Summary:** Firmware uses doorbell/parameter interface @ 0xB800C000 for display-related commands. Register layout: +0x00 (command/status with bit 0 = busy), +0x10 (param1), +0x14 (param2), +0x18 (param3), +0x1C (param4). Pattern: poll busy bit, write 4 parameters, write command to trigger operation.
- **Evidence:**
  - E1: Doorbell usage pattern: ldr r12,[0x270188] loads base 0xB800C000, then polls status @ +0x0 (tst r10,#0x1; bne wait_loop), writes params to +0x10/14/18/1C, writes command to +0x0 to trigger; source_type=ghidra; function_address=0x270040; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Literal @ 0x00270188 contains address 0xB800C000; source_type=other [ghidra-v1]
  - E3: N32903 peripheral addressing (doorbell register not in standard peripheral map, likely custom/undocumented); source_type=pdf [ghidra-v1]
- **Tags:** mmio, doorbell, display, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:13:42.231909Z
- **Updated:** 2025-12-02T03:05:16.214764Z

### E-RKO-MMIO-003: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
- **RE-KB ID:** finding-0006
- **Status:** verified
- **Type:** behavior
- **Summary:** Display controller @ 0xB100D000 used for hardware display updates with wait-for-ready pattern (poll bit 0 until clear, write color/coordinate data, set bit 0 to trigger). GPIO base @ 0xB8001000 (GP_BA) accessed indirectly with port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Per-port register offsets: OMD=+0x10, PUEN=+0x14, DOUT=+0x18, PIN=+0x1C.
- **Evidence:**
  - E1: Hardware display update routine uses literal @ 0x00230F34 (value 0xB100D000). Waits for bit 0 clear, writes display data, sets bit 0 to trigger update.; source_type=ghidra; function_address=0x230e04; function_name=hw_display_update; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: GPIO base 0xB8001000 accessed with indirect addressing pattern. Port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Register offsets per port: OMD=+0x10 (Output Mode), PUEN=+0x14 (Pull-Up Enable), DOUT=+0x18 (Data Output), PIN=+0x1C (Pin Input); source_type=other [ghidra-v1]
  - E3: GPIO control register map shows GP_BA = 0xB8001000 with register layout matching firmware usage; source_type=pdf; page=646 [ghidra-v1]
- **Tags:** mmio, display, gpio, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:14:06.741544Z
- **Updated:** 2025-12-02T03:05:27.684680Z

### E-RKO-MMIO-004: MMIO UART Controller (UA_BA @ 0xB8008000)
- **RE-KB ID:** finding-0007
- **Status:** verified
- **Type:** behavior
- **Summary:** UART peripheral base is UA_BA @ 0xB800_8000–0xB800_8FFF per N3290x memory map. Datasheet section 6.22 documents two UART channels (UART0 high-speed with flow control, UART1 normal-speed). Firmware scalar searches in both ZK-INKJET-NANO-APP.bin and ZK-INKJET-NANO-BOOT.bin show no direct accesses to this base, implying UART is likely unused in these builds.
- **Evidence:**
  - E1: Memory map shows UA_BA @ 0xB800_8000 - 0xB800_8FFF for UART Control Registers; source_type=pdf; page=48 [ghidra-v1]
  - E2: UART controller overview and dual-channel description (UART0 high-speed with CTS/RTS, UART1 normal speed); source_type=pdf; page=750 [ghidra-v1]
  - E3: Ghidra scalar search for 0xB8008000 returned 0 matches (no firmware register touches observed); source_type=ghidra; function_address=0x0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Bootloader image also has no scalar references to UA_BA; source_type=ghidra; function_address=0x0; program_name=ZK-INKJET-NANO-BOOT.bin; domain_file_id=7f011a9c518283402470126 [ghidra-v1]
- **Tags:** mmio, uart, verified
- **Confidence:** 1.0
- **Component:** uart
- **Created:** 2025-11-27T00:14:06.870516Z
- **Updated:** 2025-12-02T03:05:37.617664Z

