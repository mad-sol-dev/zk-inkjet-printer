# MMIO Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1-Recent > E1 > E3-Old > E4 (E2 = context only).

---

## CL-MMIO-REC-001: GCR_BA Base At 0xB0000000

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The Global Control Register base (GCR_BA) is 0xB0000000 and includes GPBFUN and clock/bus control registers.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (GCR_BA at SYS_BA, GPBFUN, AHB/APB controls)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-MMIO-001 (GCR_BA access patterns) [ghidra-v1]
- **E4:** E-OLD-MMIO-001, E-OLD-MMIO-007 (GCR_BA and clock control) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-MMIO-001
- E4: CL-OLD-MMIO-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Match firmware register offsets to BSP definitions in the optimized project.

**Tags:** mmio, gcr, clock

---

## CL-MMIO-REC-002: GPIO_BA Base And Port Offsets

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** GPIO_BA is 0xB8001000 with port offsets A=0x00, B=0x10/0x40 (per BSP), and per-port registers OMD/PUEN/DOUT/PIN.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (GPIO_BA=0xB8001000, port register offsets)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-MMIO-003 (GPIO base and offsets) [ghidra-v1]
- **E4:** E-OLD-MMIO-004 (GPIO offsets) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-MMIO-003 (partial overlap)
- E4: CL-OLD-MMIO-003 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm port offset usage in firmware via optimized disassembly.

**Tags:** mmio, gpio, base

---

## CL-MMIO-REC-003: BLT_BA Base At 0xB100D000

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** The BitBlt engine base address is 0xB100D000 and is used for display updates.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (BLT_BA=0xB100D000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-MMIO-003 (display update routine uses 0xB100D000) [ghidra-v1]
- **E4:** E-OLD-MMIO-003 (display controller base) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-MMIO-003 (partial overlap)
- E4: CL-OLD-MMIO-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify whether VPOST_BA (0xB1002000) is also used in firmware.

**Tags:** mmio, blt, display

---

## CL-MMIO-REC-004: SPI0_BA Base At 0xB800C000 (Not Doorbell)

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** 0xB800C000 is the SPI0 base address per BSP; E3-Old doorbell interpretations likely refer to SPI0 register access.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (SPI0_BA=0xB800C000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-MMIO-002 (doorbell access at 0xB800C000) [ghidra-v1]
- **E4:** E-OLD-MMIO-002 (doorbell block at 0xB800C000) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-MMIO-002
- E4: CL-OLD-MMIO-002

**Superseded Evidence:** Doorbell/parameter block interpretation superseded by BSP SPI0_BA definition.

**Contradictions Resolved:** None

**Next Test:** Map the firmware access pattern to SPI0 register offsets (TX0/TX1/TX2/TX3).

**Tags:** mmio, spi0, base

---

## CL-MMIO-REC-005: UART_BA Base At 0xB8008000 With No Direct References

**Status:** supported
**Confidence:** 0.80
**Authority:** E0

**Statement:** The UART base is 0xB8008000 per BSP, but direct scalar references are not observed in firmware.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (UART_BA=0xB8008000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-MMIO-004 (no direct references found) [ghidra-v1]
- **E4:** E-OLD-MMIO-006 (UART base hypothesis) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-MMIO-004
- E4: CL-OLD-MMIO-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Search for MOV/MOVT patterns that compute 0xB8008000.

**Tags:** mmio, uart, base

---

## CL-MMIO-REC-006: 0xB1006800 Mapping Is A False Positive

**Status:** supported
**Confidence:** 0.75
**Authority:** E4

**Statement:** The prior 0xB1006800 mapping is a false positive; no firmware references were found.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-MMIO-005 (false positive correction) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-MMIO-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-run scalar searches in the optimized Ghidra project to confirm.

**Tags:** mmio, correction, base
