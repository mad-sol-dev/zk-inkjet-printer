# Project History

**Timeline:** October 2025 - January 2026  
**Goal:** Enable USB-CDC interface for automatic lithium cell labeling  
**Hardware:** ZK-INKJET handheld printer (CHIKY ZK-1696 clone)

---

## October 2025: Initial Investigation

**2025-10-09: Hardware teardown and first clues**
The project began with a careful PCB inspection and SD-card imaging. The board
carried a "DWIN M5" marking, but firmware strings hinted at the older W55FA93
family. The SD card quickly revealed itself as the boot medium, and APP.bin was
recognized as a proprietary resource container rather than a typical ELF.
Early UI blob extraction and QVGA reconstruction gave the first glimpse into
how the device stores its graphics and menus, setting a practical path toward
understanding user-facing flows.

The earliest storage snapshots also showed that the SD layout was not a simple
partition table. Some artifacts looked like legacy filesystem remnants, which
raised an early caution: only direct offset validation would be trusted going
forward. That skepticism later paid off when the FAT volume mapping needed to
be reconciled with raw boot offsets.

**2025-10-10: Boot context and execution mode questions**
Initial Ghidra work uncovered a persistent ARM/Thumb context ambiguity that made
some disassembly unreliable. At the same time, early I/O mapping notes and
queue/flash-guard observations hinted that update handling was more complex than
a simple FAT copy. This was an early signal that precise address mapping and
boot sequencing would need ground-truth validation later in the project.

The October work closed with a tentative boot sequence hypothesis but a clear
understanding that runtime addresses, file offsets, and mirrored regions would
have to be disentangled before any patching could be considered safe.

---

## November 2025: Deep Dive into Firmware

**2025-11-03: SoC identity confirmed, update risk understood**
Cross-referencing board markings with datasheets confirmed the SoC as the
Nuvoton N3290X series. The legacy W55FA93 strings were reinterpreted as family
heritage rather than the exact part number, grounding all later MMIO mapping.
String analysis also showed update paths without CRC or signature checks, a
critical realization for later USB-CDC patch planning because it suggested a
permissive update pipeline.

This confirmation also narrowed the hardware feature set and ruled out several
false leads. Knowing the exact family meant that pinouts, USB controller blocks,
and memory maps could be referenced with confidence rather than guesswork.

**2025-11-26: Evidence-first workflow established**
By late November, the analysis shifted toward structured, evidence-backed
documentation. Findings were organized, and vendor documentation was cross-read
against firmware artifacts. This helped turn scattered notes into a coherent
narrative and made it possible to track corrections as understanding matured.

**2025-11-27: Update UI and USB file processing become tangible**
Dispatch-table analysis verified the upgrade UI handlers, transforming the
update flow from speculation into a mapped control path. In parallel, USB file
processing strings revealed BMP, CSV, and upgrade file handling, which reframed
USB as more than a storage channel and highlighted concrete entry points for
remote control behavior.

The USB remote-control thread became especially significant: it showed that a
software-only workflow might be possible by placing carefully formatted files on
the exposed drive. That insight kept the USB-CDC goal alive even before a custom
protocol was understood.

**2025-11-28: USB workflow corrected and trigger discovered**
A boot-time hold-key update trigger was identified, clarifying how updates are
initiated before the UI is active. The device was also corrected from USB-host
assumptions to USB MSC device mode. This pivot was pivotal: it explained why the
"MINI" drive appears over USB, and it reshaped the automation strategy toward
device-mode staging rather than external thumb-drive injection.

Menu-based triggers were also aligned with localized strings, which clarified
how the UI entries map to firmware handlers. This turned the update and print
flows into concrete, reproducible sequences rather than hypothetical paths.

---

## December 2025: System Architecture Emerges

**2025-12-01: Printhead control chain documented**
The HP45 cartridge hardware chain came into focus, mapping HA/HP lines, MOSFET
stages, and the firmware patterns that drive nozzle firing. This connected
low-level MMIO access patterns to real hardware behavior and clarified the
constraints for any future firmware modifications.

By tying the nozzle matrix behavior to actual control lines, the project moved
from a black-box printing model to a concrete, timing-aware view of how dots are
fired. That clarity later informed which firmware areas were safe to touch for
USB work without destabilizing the print pipeline.

**2025-12-02: USB-CDC patch planning begins**
Early CDC planning identified a candidate descriptor blob and enumerated USB
controller base references. While later corrections were needed, this milestone
set the direction for a USB-CDC strategy and anchored the search for endpoint
configuration code.

Those early references eventually pointed to BSP-verified USB bases, and they
created a checklist of what had to be proven in code before any CDC patch could
be considered safe.

**2025-12-15: RAW SD write chain discovered**
A full raw-write chain surfaced, showing an update path that stages files from
`3:/` to `0:/` before writing to raw SD offsets. TurboWriter evidence linked the
boot offsets 0x200 and 0x100000 to the live boot chain. These findings shifted
attention toward validating the SD layout and reconciling contradictions in
volume mapping.

Alignment checks and sector-based writes showed that updates were handled at the
block layer rather than through FAT metadata alone. TestDisk recovery of deleted
BOOT/APP files hinted that staging volumes contained remnants of past updates,
foreshadowing the Volume 2/Volume 3 clarification later verified in Phase A.

**2025-12-21: ADC mapping verified**
The ADC base was corrected to 0xB800E000, and channel assignments were aligned
with the About screen readouts. This resolved earlier mislabels and reinforced
the practice of validating UI-reported values against firmware sources.

The encoder block at 0xB8003000 remained ambiguous, but the investigation
established that the encoder path is distinct from the touch ADC pipeline. This
kept the focus on verified signals while leaving the encoder behavior as a
targeted open question rather than a guess.

**2025-12-27: Mixed-mode execution and MMIO map extracted**
ARM/Thumb mixed-mode execution was confirmed, resolving the ambiguity first
noticed in October. A BSP-derived MMIO register map was extracted, providing a
firm foundation for subsequent work on USB, ADC, and timer peripherals.

The register map also helped separate USB device and host bases, reducing a key
source of confusion when tracing controller usage in APP.bin.

**2025-12-28: Repository prepared for public sharing**
The repository was anonymized and reorganized for broader use. Documentation was
normalized and indexed, creating a stable baseline for Phase A verification and
future Phase B firmware work.

This cleanup marked a shift from exploratory notes to a structure that could be
shared and maintained, ensuring the next phase would build on a consistent body
of evidence.

---

## January 2026: Ground Truth Verification

**2026-01-05: Phase 1 completion**
A reconciliation pass of 189 initial claims yielded 152 verified facts across
nine subsystems. This checkpoint established a trusted baseline and highlighted
which areas still required empirical validation.

It also clarified the remaining risk: storage mapping and boot-offset details
were too important to leave in a speculative state, prompting the focused Phase
A ground-truth effort.

**2026-01-07: Phase A - SD image ground truth**
Phase A completed a full SD image verification and locked in several critical
facts. The boot header was confirmed as a 32-byte IBR structure at offset 0x200
with a 0xA5 [ZBW...WBZ] 0xA5 pattern, correcting the earlier contiguous-string
assumption. Three FAT volumes were mapped and verified at offsets 0x04000000,
0x24007E00, and 0x2A61BE00. The third volume, labeled "MINI" and 64 MB in size,
was confirmed as an empty user update input area rather than a firmware store.
Update workflow understanding was corrected: files are placed on Volume 3, the
IBR header is prepended to BOOT.bin, the data is written to raw offsets, and the
files are deleted afterward. Confidence rose to High, with system understanding
measured at roughly 85%.

Phase A also reconciled where firmware copies truly live. BOOT.bin and APP.bin
were confirmed at raw offsets, while deleted copies recovered from Volume 2
explained earlier confusion about Volume 3. This correction closed a major gap
in the update narrative and made the storage story internally consistent.

---

## Current Status (2026-01-08)

System understanding is **85% complete** with high confidence in the boot chain
and SD layout. The next phase shifts to firmware analysis and USB controller
validation, focused on verifying FatFS mount mappings, tracing the USB device
controller usage around **USBD_BA = 0xB1008000**, and mapping the update system
code path in the main firmware. The USB-CDC goal remains viable but now rests on
solid storage and boot ground truth.

Phase B is expected to confirm which volume indices map to the verified SD
regions, locate the USB controller initialization path, and determine how
endpoint descriptors and class requests are configured at runtime.

Key open questions include the exact mapping of `0:/` and `3:/` to SD regions,
the precise control flow for update validation, and where the firmware sets USB
endpoint configurations needed for CDC.

---

## What We Got Wrong

**Descriptor patch location (November 2025)**
A descriptor patch was first attempted at file offset 0x275140, which caused a
brick. Later work showed that the correct descriptor region lives at virtual
address 0x00475148, highlighting how file offsets and runtime addresses diverge
in this firmware and why careful VA mapping is mandatory before patching.

**LOW_MIRROR confusion (November 2025)**
A low-memory mirror initially produced duplicate functions in Ghidra, leading to
misaligned assumptions about code layout. This was resolved by separating the
mirror region from true execution addresses and by confirming mixed ARM/Thumb
execution, which removed many false positives.

**Volume 3 role and firmware storage (December 2025 - January 2026)**
Volume 3 was originally treated as a firmware storage area. Phase A proved it is
the empty user update input, while actual firmware copies were recovered as
deleted files in Volume 2. This corrected the update narrative and clarified
why the MINI drive appears empty in normal operation.

**IBR header format (January 2026)**
The boot header signature was initially described as a contiguous "ZBWp1WBZ"
string. Phase A revealed the correct spaced marker format, framed by 0xA5 bytes
in a 32-byte IBR header. This correction underscored the need for binary-level
verification rather than relying on string scans alone.
