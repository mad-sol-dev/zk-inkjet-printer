# BOOT Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-BOOT-001: BOOT.bin Sets CPU Modes And Stack Pointers
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** BOOT.bin uses CPSR mode writes and literal stack pointers to initialize per-mode stacks early in execution.
- **Evidence:**
  - E4: E-OLD-BOOT-001 (CPSR + stack initialization)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Disassemble current BOOT.bin build to confirm offsets and stack values.
- **Tags:** boot, cpsr, stack
- **Cross-Reference:** None (unique)

## CL-OLD-BOOT-002: BOOT.bin Relocates Vectors Before Branching
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** BOOT.bin contains a relocation routine that copies vector data and branches to a relocated entry point.
- **Evidence:**
  - E4: E-OLD-BOOT-002 (relocation routine evidence)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Identify the relocation target in BOOT.bin and confirm runtime control transfer.
- **Tags:** boot, relocation, vectors
- **Cross-Reference:** None (unique)

## CL-OLD-BOOT-003: BOOT.bin Issues Display Init Command IDs
- **Status:** hypothesis
- **Confidence:** 0.55
- **Statement:** BOOT.bin issues a display init sequence using command IDs (0x2A..0xE0) aligned with DWIN/T5L display protocols.
- **Evidence:**
  - E4: E-OLD-BOOT-003 (display init constants)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Match the constants to a vendor command table and trace the write routine.
- **Tags:** boot, display, init, hypothesis
- **Cross-Reference:** None (unique)

## CL-OLD-BOOT-004: BOOT.bin Toggles Cache/MMU Via CP15
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** BOOT.bin includes CP15 mrc/mcr sequences for cache/MMU control during early init.
- **Evidence:**
  - E4: E-OLD-BOOT-004 (CP15 control sequence)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Confirm CP15 register targets and bitfields with ARM926 documentation.
- **Tags:** boot, cp15, cache, mmu
- **Cross-Reference:** E1 CL-SOC-007 (partial overlap)
