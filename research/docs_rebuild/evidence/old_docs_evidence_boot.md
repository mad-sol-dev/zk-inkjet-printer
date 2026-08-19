# BOOT Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-BOOT-001: BOOT.bin CPU Mode/Stack Initialization
- **Content:** BOOT.bin shows `msr CPSR_c` sequences and loads per-mode stack pointers from a literal table near 0x40.
- **Source:** old_docs/analysis/boot_analysis_methodology.md#4-Entry--Stack-Initialisation-Verification
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** boot, cpsr, stack, arm

### E-OLD-BOOT-002: Relocation Routine Copies Vectors
- **Content:** BOOT.bin copies PC-relative vectors via ldm/stm and branches to the relocated entry, with targets at 0x3068/0x30A8.
- **Source:** old_docs/analysis/boot_analysis_methodology.md#6-Relocation-Routine-Evidence
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** boot, relocation, vectors

### E-OLD-BOOT-003: Display Init Command IDs In Boot
- **Content:** BOOT.bin issues constants 0x2A..0xE0 in a display init sequence consistent with DWIN/T5L command IDs.
- **Source:** old_docs/analysis/boot_analysis_methodology.md#10-Peripheral--Display-Setup
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** boot, display, init, commands

### E-OLD-BOOT-004: CP15 Cache/MMU Control In BOOT.bin
- **Content:** BOOT.bin contains CP15 mrc/mcr sequences that toggle cache/MMU settings during early init.
- **Source:** old_docs/analysis/boot_analysis_methodology.md#5-Cache-Control-CP15-Confirmation
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** boot, cp15, cache, mmu
