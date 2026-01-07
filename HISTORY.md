# History (public)

This history is evidence-driven. Sessions are handoff notes; claims are linked to chat transcript evidence. Claim statuses are taken from `research/CLAIMS.md`.

## Phase 1: Early identity signals (Oct 2025)
- The SoC was reported as marked "DWIN M5," while the firmware contains the string "W55FA93 USB Card Reader 1.00" (CL-002, supported). This established a mismatch between PCB marking and firmware identifiers, not a final identity.
- Firmware string extraction showed update file paths under 3:/ (CL-013, supported), hinting at a structured update pipeline but not yet mapping volumes.

Turning point: evidence in transcripts started to separate marking from silicon identity, and update paths started to look systematic rather than ad-hoc.

## Phase 2: USB/SD/update architecture (Dec 2025)
- A consolidated summary described USB VID/PID pairs, IBR boot behavior, SD layout, and update flow (CL-003, CL-004, CL-005, CL-006, supported). These claims remain supported, not verified, pending direct device capture and image inspection.
- Boot flow notes described BOOT.bin loading APP.bin to 0x03000000 with no CRC/size check (CL-007, CL-008, supported). The absence of a checksum is supported by the padding test, but still needs repeat confirmation.

Turning point: the project shifted from isolated strings to a coherent boot/update model, with explicit tests used as evidence.

## Phase 3: Descriptor offset correction (Dec 2025)
- A patch at file offset 0x275140 was initially treated as a descriptor edit and caused a brick (CL-009, refuted).
- Subsequent analysis identified string descriptors at VA 0x00475148 and config/interface data around 0x00475140 (CL-010, CL-011, supported). This corrected the earlier offset mistake.

Turning point: the descriptor region was re-mapped with explicit byte dumps, preventing further blind patches.

## Phase 4: Hardware mapping and analysis hygiene (late Dec 2025)
- Touch panel wiring was reported as using dedicated ADC_TP pins (CL-014, supported). This clarified why generic ADC channel reads did not explain touch behavior.
- A low-memory mirror (LOW_MIRROR) was identified as a source of duplicate functions in Ghidra analysis (CL-012, supported). This led to methodological cleanup steps rather than new device claims.

Turning point: focus expanded from firmware-only clues to hardware wiring and analysis quality controls.

## What we got wrong and how we corrected it
- USB descriptor patch location: The assumption that offset 0x275140 was a safe descriptor region led to a brick (CL-009, refuted). Byte dumps showed descriptors start at VA 0x00475148 and config/interface data around 0x00475140 (CL-010, CL-011, supported).
- Runtime vs analysis base addresses: APP.bin load address (0x03000000) and analysis base (0x00200000 with mirror) remain in tension (CL-007 vs CL-012). This is still an open mapping question rather than a resolved correction.

## Current state (evidence-based)
- SoC identity is supported as N32903U5DN/W55FA93 family (CL-001), with a separate marking discrepancy (CL-002).
- USB/SD/update architecture is supported but needs direct capture/verification (CL-003 through CL-008).
- Descriptor region mapping is corrected and supported (CL-010, CL-011).

For detailed evidence pointers, see `research/CLAIMS.md` and `research/MASTER_TIMELINE.md`.
