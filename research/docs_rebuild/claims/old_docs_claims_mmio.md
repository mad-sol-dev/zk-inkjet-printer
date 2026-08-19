# MMIO Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-MMIO-001: GCR_BA Base And GPBFUN Accesses
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** Firmware accesses GCR_BA at 0xB0000000 and manipulates GPBFUN (0xB0000084) and clock/bus control registers via read-modify-write patterns.
- **Evidence:**
  - E4: E-OLD-MMIO-001 (GCR_BA usage)
  - E4: E-OLD-MMIO-007 (clock/bus register touches)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Confirm register offsets against the N32903 datasheet.
- **Tags:** mmio, gcr_ba, gpbfun, clock
- **Cross-Reference:** E3-Old CL-RKO-MMIO-001 (exact match)

## CL-OLD-MMIO-002: Doorbell Parameter Block @ 0xB800C000
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** Firmware uses a doorbell/parameter block at 0xB800C000 with busy-bit polling and four parameter registers.
- **Evidence:**
  - E4: E-OLD-MMIO-002 (doorbell layout + usage pattern)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Identify the full command set used in the doorbell interface.
- **Tags:** mmio, doorbell, display
- **Cross-Reference:** E3-Old CL-RKO-MMIO-002 (exact match)

## CL-OLD-MMIO-003: Display Controller And GPIO Base Maps
- **Status:** verified
- **Confidence:** 0.93
- **Statement:** Display controller base is 0xB100D000 and GPIO base is 0xB8001000 with port/reg offsets (OMD/PUEN/DOUT/PIN).
- **Evidence:**
  - E4: E-OLD-MMIO-003 (display base)
  - E4: E-OLD-MMIO-004 (GPIO base/offsets)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Confirm display register semantics via vendor docs or runtime capture.
- **Tags:** mmio, display, gpio
- **Cross-Reference:** E3-Old CL-RKO-MMIO-003 (exact match)

## CL-OLD-MMIO-004: 0xB1006800 Is A False Positive
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** Old docs retract a prior 0xB1006800 mapping; no firmware refs were found and the doorbell base is 0xB800C000.
- **Evidence:**
  - E4: E-OLD-MMIO-005 (false positive correction)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Re-run scalar searches on current binaries to confirm no 0xB1006800 usage.
- **Tags:** mmio, correction, doorbell
- **Cross-Reference:** E3-Old CL-RKO-MMIO-002 (partial overlap)

## CL-OLD-MMIO-005: UART Base Hypothesis @ 0xB8008000
- **Status:** hypothesis
- **Confidence:** 0.55
- **Statement:** UART controller base is likely 0xB8008000 per N32903 memory map, but firmware references were not observed.
- **Evidence:**
  - E4: E-OLD-MMIO-006 (UART base hypothesis)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Search for computed address patterns (MOV/MOVT) that derive 0xB8008000.
- **Tags:** mmio, uart, hypothesis
- **Cross-Reference:** E3-Old CL-RKO-MMIO-004 (exact match)
