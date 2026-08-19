# HP45 Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-HP45-001: Printhead Drivers Use LVDATA Bus
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** Printhead driver ICs are wired to LVDATA lines on GPC[0-15], indicating the printhead data path reuses the SoC's LCD/LV data bus pins.
- **Evidence:**
  - E4: E-OLD-HP45-001 (GPC[0-15] mapped to printhead drivers)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Trace one LVDATA pin to confirm connectivity to a printhead driver input.
- **Tags:** hp45, printhead, lvdata, gpio
- **Cross-Reference:** E1 CL-HARDWARE-002 (partial overlap)

## CL-OLD-HP45-002: Printhead Control Lines Occupy GPA/GPD/GPB Pins
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** Printhead control signals occupy GPA[0-7], GPB[15], and GPD[5-12] pins connected to printhead driver ICs.
- **Evidence:**
  - E4: E-OLD-HP45-002 (GPA/GPD/GPB printhead connections)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Confirm two of the listed pins with continuity probing.
- **Tags:** hp45, printhead, gpio, pinout
- **Cross-Reference:** E1 CL-HARDWARE-002 (partial overlap)
