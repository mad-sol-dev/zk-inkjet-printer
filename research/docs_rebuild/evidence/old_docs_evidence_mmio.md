# MMIO Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-MMIO-001: GCR_BA Base And GPBFUN Usage
- **Content:** GCR_BA at 0xB0000000 is accessed repeatedly; GPBFUN (0xB0000084) and clock/bus control (0xB0000204) are manipulated with read-modify-write patterns.
- **Source:** old_docs/findings/mmio_map.md#0xB0000000---GCR_BA-Global-Control-Register
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, gcr_ba, gpbfun, clock-control
- **Note:** [ghidra-v1]

### E-OLD-MMIO-002: Doorbell/Parameter Block @ 0xB800C000
- **Content:** A doorbell interface at 0xB800C000 uses +0x00 for busy/command and +0x10..+0x1C for four parameters; firmware polls bit 0 then writes params and command.
- **Source:** old_docs/findings/mmio_map.md#0xB800C000---DoorbellParameter-Block
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, doorbell, display, parameter-block
- **Note:** [ghidra-v1]

### E-OLD-MMIO-003: Display Controller Base @ 0xB100D000
- **Content:** Display update routine uses base 0xB100D000, waits for bit 0 to clear, writes data, then sets bit 0 to trigger updates.
- **Source:** old_docs/findings/mmio_map.md#0xB100D000---Display-Controller
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, display, controller
- **Note:** [ghidra-v1]

### E-OLD-MMIO-004: GPIO Base @ 0xB8001000
- **Content:** GPIO base uses port offsets A=0x00, B=0x40, C=0x80, D=0xC0 with register offsets OMD=0x10, PUEN=0x14, DOUT=0x18, PIN=0x1C.
- **Source:** old_docs/findings/mmio_map.md#0xB8001000---GP_BA-GPIO-Base
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, gpio, gp_ba, offsets
- **Note:** [ghidra-v1]

### E-OLD-MMIO-005: False Positive Correction (0xB1006800)
- **Content:** No firmware references exist for 0xB1006800; the correct doorbell base is 0xB800C000.
- **Source:** old_docs/findings/mmio_map.md#Corrected-False-Positives
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, correction, doorbell

### E-OLD-MMIO-006: UART Base Hypothesis @ 0xB8008000
- **Content:** UART controller is hypothesized at 0xB8008000 per N32903 architecture, pending direct register access confirmation.
- **Source:** old_docs/findings/mmio_map.md#Hypotheses-Needs-Verification
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** mmio, uart, hypothesis

### E-OLD-MMIO-007: Clock/Bus Control Register Touches
- **Content:** Firmware toggles clock/bus control registers at 0xB0000204/0xB0000208/0xB0000014/0xB0000018 during init.
- **Source:** old_docs/reference/mmio_fingerprint.md#ClockBus-Control-0xB0000xxx---VERIFIED
- **Date:** 2025-11-03
- **Type:** REFERENCE
- **Provenance:** None
- **Tags:** mmio, clock-control, init
- **Note:** [ghidra-v1]
