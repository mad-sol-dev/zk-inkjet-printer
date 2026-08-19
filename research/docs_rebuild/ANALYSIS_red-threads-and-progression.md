# Analysis: Red Threads and Progression (2025-10-09 to 2025-12-28)

## Overview of session timeline
- 2025-10-09: Archived early boot/resource/UI reconstruction work; SD card boot medium; APP.bin as proprietary resource container; UI QVGA decode pipeline.
- 2025-10-10: Ghidra headless workflow established; Thumb/ARM context problem surfaced; upgrade I/O mapping and queue/flash-guard notes captured.
- 2025-11-03: SoC identification confirmed (Nuvoton N3290X); UTF-16LE USB strings in APP.bin; update path lacks CRC/signature checks.
- 2025-11-26: MCP integration test for Ghidra/re-kb/pdf; fixed .re_kb/select_this_project.sh; created finding-0001; documented helper tools.
- 2025-11-27: Dispatch table analysis verified upgrade UI handlers; finding-0010 promoted to verified with dispatch table evidence.
- 2025-11-27: USB remote control discovery; created finding-0012; identified BMP/CSV/upgrade paths and USB file processing strings.
- 2025-11-28: USB trigger follow-up; traced string clusters and dispatch table indirections; boot-time hold-key trigger documented in finding-0013.
- 2025-11-28: USB trigger follow-up 2; corrected USB architecture to MSC device mode; runtime menu-based triggers added to finding-0013.
- 2025-12-01: re-kb tool debug; updated finding-0001; created HP45 findings 0014-0018; updated finding-0012; commits made.
- 2025-12-01: re-kb tool test; validated create/update flows; HP45 chain reinforced; finding-0018 updated with MMIO patterns.
- 2025-12-02: USB CDC patch plan drafted; descriptor blob replacement at 0x475140; UDC base 0xB8007000 enumerated.
- 2025-12-15: RAW SD write chain discovered; update flow 3:/ -> 0:/ -> RAW; finding-0023 update blocked by re-kb validation bug.
- 2025-12-15: Session handoff established boot architecture shift; TurboWriter evidence for offsets 0x200 and 0x100000; volume mapping anomalies noted.
- 2025-12-15: REF_storage-topics-inventory captured facts vs speculation and volume assignment contradictions (finding-0020/0023).
- 2025-12-21: ADC channel mapping completed; base corrected to 0xB800E000; encoder block at 0xB8003000 identified; finding-0031 updated.
- 2025-12-27: ARM/Thumb mixed-mode confirmed; BSP MMIO register map extracted; findings 0001/0002 recorded; n32903_registers.json produced.
- 2025-12-27: BSP MMIO extraction quick log; initial output landed in .re_kb (later corrected to research/findings/).
- 2025-12-27: Repository restructure planning; CLAUDE.md rewrite and MIGRATION_PLAN.md produced.
- 2025-12-28: Repository anonymization and security cleanup; session logs normalized; INDEX.md/README.md created; .gitignore hardened.

## Technical Red Threads

### USB/CDC implementation progress
- 2025-11-03: USB descriptor strings in APP.bin expose Nuvoton/W55FA93; base for USB stack context in finding-0001.
- 2025-11-27: finding-0012 collects HP45-related strings plus USB file processing paths; BMP and CSV handling identified as viable injection routes.
- 2025-11-27: remote-control attack vectors enumerated (BMP pipeline, CSV injection, upgrade hijack, custom handler), framing later trigger work.
- 2025-11-27: upgrade-related handlers tied to dispatch table (finding-0010) confirm USB-based update UI pipeline.
- 2025-11-28: initial USB trigger hunt shows menu strings nearby but no direct xrefs; indirection through dispatch table persists.
- 2025-11-28: localization strings (German/Dutch) used to align dispatch table entries with UI menu actions.
- 2025-11-28: finding-0013 documents boot-time hold-key update trigger (maybe_update_from_udisk @ 0x0026887C).
- 2025-11-28: update_copy_or_flash called twice (BOOT then APP) per boot-time evidence chain, clarifying trigger scope.
- 2025-11-28: follow-up 2 corrects assumption from USB host to USB MSC device; MINI volume exposure via USB menu added to finding-0013.
- 2025-11-28: device cannot accept external USB sticks; USB cable + menu activation is required to stage files.
- 2025-11-28: requirement shift toward automation without touch input introduced start-signal and auto-trigger constraints.
- 2025-11-28: runtime BMP printing flow established (File -> USB -> Browse -> Start); no filename pattern needed in device-mode flow.
- 2025-12-02: CDC patch plan proposes replacing 236-byte descriptor blob at 0x475140; UDC base 0xB8007000 references enumerated.
- 2025-12-02: endpoint config discovery still pending; need control request handler for CDC class codes (0x20/0x21/0x22).
- 2025-12-15: staging (3:/ -> 0:/) clarifies how USB-delivered files reach RAW sectors, shaping CDC patch delivery options.
- 2025-12-15: storage pipeline clarifies how firmware files reach RAW sectors; relevant for CDC patch deployment strategy.
- 2025-12-27: BSP MMIO extraction lists USB_BA/USBD_BA/USBH_BA bases; intended to anchor CDC stack analysis (finding-0002).
- 2025-12-27: USB device vs host register bases separated (USB_BA/USBD_BA vs USBH_BA), reducing ambiguity in stack tracing.
- 2025-12-27: ARM/Thumb mix implies USB handlers may be split across modes; impacts pattern searches for CDC hooks.
- 2025-12-28: anonymization preserves USB-related findings while removing MCP secrets; public-ready data for future CDC work.

### Storage and filesystem understanding evolution
- 2025-10-09: SD card identified as boot medium; stage-1/2 loaders and APP.bin resource container notes captured.
- 2025-10-09: ext4 remnants noted as legacy/unrelated; early caution about stale artifacts in SD image.
- 2025-11-03: update path traced to sd_write_blocks; early recognition of no checksum validation.
- 2025-11-27: update file literal pool at 0x0037E820 used for USB upgrades; no CRC noted again (finding-0010 thread).
- 2025-11-28: boot-time hold-key scanning loops at 0x0025A930/0x0025A990/0x0025A9F0 documented (finding-0013).
- 2025-12-15: RAW SD write chain discovered (FUN_0006887c -> 0006ccf8 -> 00032500 -> 00094584); update writes to sectors 1 and 2048.
- 2025-12-15: FUN_00032500 enforces 0x200-byte alignment and converts byte offsets to LBA; RAW writes are sector-aligned only.
- 2025-12-15: TestDisk shows deleted BOOT/APP entries in FAT; reinforces staging workflow prior to RAW copy.
- 2025-12-15: staging rationale defined (3:/ user -> 0:/ system) to isolate RAW writes; no internal flash present.
- 2025-12-15: handoff explains TurboWriter evidence for offsets 0x200/0x100000; boot sequence uses RAW reads pre-FatFS.
- 2025-12-15: disk_ioctl sector counts (drive0=0x100000 sectors, drive3=0x20000 sectors) introduce a size mismatch to partition scans.
- 2025-12-15: REF_storage inventory lists contradictions in volume mapping (0:/ vs 3:/ vs MINI) and about-screen 0.8/3.8 GB ambiguity.
- 2025-12-15: re-kb validation bug blocks finding-0023 status change; storage facts preserved in session logs.
- 2025-12-15: storage findings 0020/0021/0023 now form the core evidence set, but require consolidation for volume mapping.
- 2025-12-21: ADC mapping confirms VIN/VADJ readings correlate with About screen; supports storage-related UI context accuracy.
- 2025-12-28: anonymized sessions consolidate storage evidence and contradictions for later consolidation work.

### Hardware reverse engineering (SoC, HP45, ADC, encoder, MMIO)
- 2025-11-03: SoC confirmed as Nuvoton N3290X (finding-0001 seed); MMIO fingerprint 0xB0000xxx/0xB800C000 noted.
- 2025-10-09: bootloader display command sequences align with DWIN/T5L behavior; hints at display controller linkage.
- 2025-11-27: HP45 cartridge control strings cluster at 0x001f2xxx; finding-0012 created for HP45 control surface.
- 2025-11-27: GPB[2-5] debug header mapped but left unconfigured; rules out UART without firmware change.
- 2025-12-01: HP45 architecture expanded into findings 0014-0018 (cartridge matrix, HA/HP lines, MOSFETs, firmware patterns).
- 2025-12-01: finding-0018 records MMIO access patterns and 22/14 parameter constants linked to HP45 control loops.
- 2025-12-01: GCR_BA access patterns used as template to locate peripheral init sequences; GPIO/display still indirect.
- 2025-12-21: ADC base corrected to 0xB800E000; channels mapped; finding-0031 verified.
- 2025-12-21: voltage function renames (VBAT -> VADJ, V3V3 -> VIN) align with About screen evidence.
- 2025-12-21: touch ADC pipeline identified as interrupt-driven; adc_touch_init and touch_adc_read mapped.
- 2025-12-21: AIN0/AIN1 verified unused; touch panel is the only ADC consumer beyond VIN/VADJ.
- 2025-12-21: V5V0 reported as constant 5.0V in code, not from ADC; clarifies About screen readout.
- 2025-12-21: encoder interface functions (encoder_read/init/config) found; 0xB8003000 block remains undocumented.
- 2025-12-27: ARM/Thumb mixed-mode confirmed; resolves early 2025-10-10 Thumb/ARM ambiguity.
- 2025-12-27: BSP MMIO register map extracted (1,544 regs) including USB_BA, GPIO_BA, ADC_BA, TMR_BA (finding-0002).
- 2025-12-27: RTC_BA listed as 0xB8003000, intersecting with encoder block and suggesting possible RTC/Timer overlap.
- 2025-12-27: register map includes BLT/SPU/JPEG, enabling later correlation with UI/graphics routines.
- 2025-12-28: register map retained in research/findings/n32903_registers.json for future label import into Ghidra.

### Tooling development (MCP, RE-KB, Ghidra)
- 2025-10-10: ghidraHeadless wrapper and helper scripts used; callgraph export blocked by Thumb context issue.
- 2025-11-26: MCP integration validated for re-kb/Ghidra/pdf; collect and search_scalars_with_context highlighted.
- 2025-11-26: .re_kb/select_this_project.sh fixed (heredoc and Python syntax) enabling re-kb activation.
- 2025-11-26: pdf-reader extraction of memory map and GPIO tables validated Ghidra scalar hits.
- 2025-11-27: re-kb attach_evidence errors (missing function_address) influenced evidence formatting choices.
- 2025-11-27: Ghidra MCP state/LOADING issues noted; request for better error reporting captured.
- 2025-12-01: re-kb read/write operations exercised heavily; creation of findings 0014-0018; updates to findings 0001/0012/0018.
- 2025-12-01: finding-0007 UART status updated with doc evidence; finding-0011 evidence and confidence raised (tools + Ghidra).
- 2025-12-01: re-kb index rebuild used to sync status; severity set to info across findings.
- 2025-12-01: schema validation blocked verified findings with pending next_steps; workflow adapted to clear next_steps first.
- 2025-12-15: re-kb validation bug (verified + next_steps) blocks finding-0023 update; tooling improvement request logged.
- 2025-12-15: Codex logs retained to corroborate complex chains; cross-checks against Ghidra used to confirm accuracy.
- 2025-12-27: BSP extraction scripted with scripts/extract_bsp_mmio_registers.py; initial file location misstep corrected.
- 2025-12-27: codex agent idle loop after completion led to explicit monitoring guidance.
- 2025-12-28: anonymization removes MCP secrets and adds .mcp.json/.mcp-stdio.json to .gitignore; tooling hygiene improved.

### Documentation and organization improvements
- 2025-10-09: analysis_traceability and boot methodology referenced as canonical navigation.
- 2025-10-09: legacy roadmap preserved for context while shifting active work to docs/findings.
- 2025-10-10: session notes consolidated; next-session briefs and reproducible commands listed.
- 2025-11-26: CLAUDE.md updated with MCP quick start and helper tools.
- 2025-11-27: findings and docs cross-referenced (update_file_rules.md, gpio_configuration.md).
- 2025-12-01: re-kb findings expanded; .gitignore updated; commits recorded with evidence updates.
- 2025-12-15: session handoff formalizes boot architecture shift and volume mapping anomalies.
- 2025-12-15: REF_storage inventory formalizes facts vs speculation and open questions.
- 2025-12-21: RE-KB finding-0031 created and verified with evidence chain.
- 2025-12-27: CLAUDE.md rewrite and MIGRATION_PLAN.md for repo restructure.
- 2025-12-27: RE-KB Club Rule #1 (never write directly to .re_kb) reinforced after a misplacement.
- 2025-12-28: session logs normalized to YYYY-MM-DD format; INDEX.md and README.md added; privacy scan artifacts recorded.
- 2025-12-28: anonymization rules and security procedures documented for future contributions.

## Key Breakthroughs (discoveries that changed direction)
- 2025-11-03: SoC identification (Nuvoton N3290X) confirmed via USB descriptor strings; foundation for all register mapping work (finding-0001).
- 2025-11-27: Dispatch table structure verified at 0x003D3E00; upgrade UI handlers validated and finding-0010 promoted to verified.
- 2025-11-27: USB file processing confirmed (BMP/CSV/update), enabling software-only remote control path (finding-0012).
- 2025-11-28: Boot-time hold-key trigger for USB update scanning discovered; shifts focus from runtime scanning to boot pipeline (finding-0013).
- 2025-11-28: USB MSC device-mode correction; replaces earlier USB-host assumption and unlocks realistic workflow via MINI volume (finding-0013).
- 2025-12-01: HP45 hardware chain documented into findings 0014-0018; establishes full cartridge control architecture.
- 2025-12-02: CDC patch plan formalized, linking descriptor blob location and UDC base addresses.
- 2025-12-15: RAW SD write chain confirmed; update workflow fully mapped (finding-0023) and single-SD architecture clarified.
- 2025-12-15: TurboWriter evidence and boot offsets (0x200, 0x100000) validated; boot sequence reinterpreted.
- 2025-12-21: ADC base correction (0xB800E000) and full channel mapping done; earlier mislabels fixed (finding-0031).
- 2025-12-27: ARM/Thumb mixed-mode confirmed; resolves 2025-10-10 disassembly ambiguity; aids precise analysis (finding-0001).
- 2025-12-27: BSP MMIO register map extracted (1,544 regs) to ground future USB/ADC/Timer analysis (finding-0002).
- 2025-12-28: repo anonymization and security cleanup unblocked public sharing and future external collaboration.

## Methodology Evolution (how the approach changed over time)
- 2025-10-09/10: exploratory reverse engineering with ad-hoc notes and manual UI reconstruction scripts.
- 2025-10-10: shift toward reproducible workflows (ghidraHeadless scripts, explicit command capture).
- 2025-11-03: evidence-driven SoC identification by combining string scans, raw memory reads, and datasheet cross-checks.
- 2025-11-26: formal MCP triad (Ghidra + re-kb + PDF) adopted; integration tests institutionalized.
- 2025-11-27: dispatch table analysis combines scalar search, read_words, and string xrefs to validate indirect call sites.
- 2025-11-28: iterative hypothesis testing for USB trigger; fallback to multi-language string search and dispatch table decoding.
- 2025-11-28: rapid correction when architecture assumption (USB host) invalidated by user data; findings updated rather than appended.
- 2025-11-28: increased user requirement framing (no-touch automation) steered analysis toward triggers and external signals.
- 2025-12-01: re-kb findings used as primary capture; creates coherent HP45 chain with evidence across hardware/docs/firmware.
- 2025-12-01: repeated re-kb update cycles highlight importance of schema validation and evidence formatting (function_address requirement).
- 2025-12-01: Ghidra MMIO pattern hunting used as heuristic to locate GPIO/display access paths (finding-0018).
- 2025-12-15: Codex-assisted deep disassembly used to map write chain; cross-verified with TestDisk and offsets.
- 2025-12-15: explicit separation of facts vs speculation created (REF_storage inventory) to prevent drift.
- 2025-12-21: decision to stop when lacking Timer docs; bias toward verified facts over speculation (encoder analysis paused).
- 2025-12-21: added process guardrails (avoid parallel Ghidra access; restart if LOADING).
- 2025-12-27: tooling scripts used to extract register maps from BSP headers; data persisted for Ghidra import.
- 2025-12-27: RE-KB workflow tightened after accidental direct .re_kb write; rule reinforced to use create_finding.
- 2025-12-28: anonymization and security processes integrated; privacy scan before public release.
- 2025-12-28: repository structure planning and naming conventions formalized to prevent drift.

## Current State (where things stand now)
- USB architecture: device operates as USB MSC device; MINI volume exposed via USB menu; no USB host support (finding-0013).
- USB triggers: boot-time hold-key update scan confirmed; runtime menu-based update/print flows documented (finding-0013).
- USB printing: BMP printing via File -> USB -> Browse is functional; filename pattern requirement removed in device-mode flow.
- CDC direction: descriptor replacement plan exists (2025-12-02); endpoint config and class request handler remain unimplemented.
- CDC prerequisites: UDC register writes and control request dispatcher mapping still missing.
- Update pipeline: firmware scans filenames via literal pool and memcmp; no checksum/CRC verification (finding-0010, finding-0021).
- Storage: RAW boot images at 0x200 and 0x100000 validated; APP loaded to 0x03000000 (finding-0021/0023).
- Storage: single physical SD card confirmed; 3:/ -> 0:/ staging logic documented (finding-0023).
- Storage: partition/volume mapping still inconsistent across sources; REF_storage inventory captures contradictions (finding-0020/0023).
- Storage: disk_ioctl volume sizes vs TestDisk partition sizes are unresolved and need empirical validation.
- SoC: Nuvoton N3290X confirmed; mixed ARM/Thumb regions mapped; foundation for instruction-level analysis (finding-0001).
- MMIO: BSP register map extracted (1,544 regs) for N32903; file stored at research/findings/n32903_registers.json (finding-0002).
- MMIO: register map import into Ghidra and struct creation remain pending tasks.
- ADC: base 0xB800E000 confirmed; channel assignments finished; VADJ/VIN naming fixed (finding-0031).
- Encoder: functions found but 0xB8003000 block not identified; analysis paused pending Timer docs.
- HP45 hardware: cartridge matrix, HA/HP pin mapping, MOSFET chain documented (findings 0014-0017).
- HP45 firmware: MMIO patterns and 22/14 constants recorded; direct print loop not yet isolated (finding-0018).
- HP45 chain: finding-0016 and finding-0018 remain in_progress; function-level entry points still needed.
- Ghidra workflow: collect, search_scalars_with_context, disassemble_batch used effectively; ARM/Thumb detection stable.
- re-kb workflow: findings expanded to 20+; index rebuild used; validation bug blocks finding-0023 status change.
- re-kb hygiene: evidence formatting and create_finding usage now standardized after earlier missteps.
- Documentation: session logs normalized and indexed; CLAUDE.md and MIGRATION_PLAN.md updated; repo ready for sharing.
- Repository status: anonymization and secret removal complete; consolidation of legacy docs into new layout remains.

## Open Questions (what is still unclear)
- Which physical button or key triggers the boot-time hold-key check (finding-0013)?
- Which volume is actually exported as USB MSC "MINI" (0:/ vs 3:/) given contradictory evidence?
- What is the authoritative mapping of partitions to FatFS volumes (finding-0020 vs ZK_TEST_README vs session logs)?
- What do the About screen values (0.8/3.8 GB) represent in terms of partition sizes or usage?
- Are volumes 1:/ and 2:/ used anywhere, or are they legacy placeholders?
- Where is the CSV voltage calibration file parsed (inkjet-lite-vadj-sample.csv)?
- What is the trigger path for runtime BMP scanning in firmware (beyond UI workflow)?
- Is there any USB command protocol beyond MSC (CDC/serial, vendor requests) hidden in the stack?
- Where in code are USB device controller endpoint configs set (UDC base 0xB8007000)?
- Which function handles CDC class requests if CDC is patched in (bRequest 0x20/0x21/0x22)?
- What is the exact role of 0xB8003000 (RTC vs timer vs encoder peripheral)?
- Which register contains the encoder count/angle value shown as "Encoder OK | 66602"?
- Where are GPIO base pointers stored if GPIO_BA is not a direct scalar (finding-0018)?
- What is the precise GPIO usage for the external start signal or physical trigger?
- Which delay routine yields ~1.8 us timing for HP45 firing sequences?
- What is the maximum safe APP.bin size given RAM headroom and update buffer constraints?
- Can the update pipeline be hardened with checksum verification without breaking boot flow?
- Should finding-0023 be split into smaller findings to bypass re-kb validation bug?
- Is 0xB8002000+0x1C (used in encoder_init_clock) a timer control register or something else?
- What is the exact volume layout on the SD image (TestDisk vs disk_ioctl mismatch)?
- Who/what writes queue_ctrl+0x10 (from 2025-10-10 notes) and how does it affect update queue control?
- Does validator 0x002BFDDC modify additional state beyond return code (2025-10-10 open question)?
