# USB Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures strategic planning, implementation roadmaps, and research context not present in E1/E3 tiers.

---

## USB Remote Control and CDC Implementation

### E2-USB-006: USB Remote Control Injection Point Analysis
- **Session ID:** S-006 (2025-11-27)
- **File:** sessions/2025-11-27_usb-remote-control-discovery.md
- **Type:** Strategic analysis
- **Summary:** Evaluation of practical injection points for USB-based remote control of the printer. Analyzed firmware update workflow, USB trigger mechanisms, and CDC implementation strategies to identify optimal approach for automatic lithium cell labeling goal.
- **Key Evidence:**
  - Boot-time hold-key detection identified as primary trigger (function @ 0x0026887C)
  - Runtime menu trigger via "OS Update"/"UI Update" menu paths
  - USB DEVICE mode (MSC) confirmed - device exposes 64MB "MINI" volume, NOT USB host
  - File-based injection workflow: PC writes to MINI volume → device copies to internal storage → processes files
  - BMP printing workflow: File → USB file browser → select BMP → editor (zoom/rotate/mirror) → Print
  - No checksum validation - files trusted by filename match
  - Strategic options evaluated: (1) USB-CDC serial interface, (2) Modified firmware update, (3) BMP injection
- **Outcome:** Remote control feasibility confirmed, CDC approach selected as most flexible
- **Research Value:** Documents decision-making process for USB-CDC implementation goal, explains project direction
- **Cross-Reference:** CL-USB-004 (USB trigger), CL-BOOT-011 (firmware update), CL-RKO-USB-001 (E3-Old trigger analysis)
- **Tags:** usb, remote-control, cdc, strategy, injection-point, msc
- **Created:** 2025-11-27
- **Evidence Tier:** E2 (strategic planning)

### E2-USB-011: CDC Patch Strategy and Risk Assessment
- **Session ID:** S-011 (2025-12-02)
- **File:** sessions/2025-12-02_usb-cdc-patch.md
- **Type:** Implementation roadmap
- **Summary:** CDC patch planning session for N32903/W55FA93 USB controller. Documented strategy for adding USB-CDC (Communications Device Class) functionality to existing MSC (Mass Storage Class) firmware. Risk assessment of binary patching vs firmware modification approaches.
- **Key Evidence:**
  - Current USB mode: MSC (VID:PID 0416:0093), EP1 IN + EP2 OUT bulk endpoints, 512-byte packets
  - IBR boot mode: VID:PID 0416:9396, EP2 IN + EP3 OUT (confirms EP3 available)
  - CDC strategy: Reuse EP1/EP2 for bulk data, add CDC control interface with EP3 INT endpoint
  - Descriptor patch locations: Device @ VA 0x475101, Config @ VA 0x475118, Strings @ VA 0x475140
  - Ghidra memory layout: image_base=0x0, FLASH block 0x200000-0x47522B (VA - 0x200000 = file offset)
  - APP.bin extensibility confirmed: Test A (+4KB patch) succeeded without bricking
  - Risk: Test B (descriptor string patch @ 0x275140) bricked device - location contained critical code
  - USB controller base: 0xB8007000 (literal @ 0x00030ab8) - **NOTE: Later proven incorrect, actual USB_BA=0xB1008000**
- **Outcome:** Conservative patch strategy adopted - string changes only before full CDC replacement
- **Research Value:** Documents implementation risks, explains why conservative patching approach needed, shows early USB base address error
- **Cross-Reference:** CL-USB-010 (USB stack), CL-RKO-USB-002 (E3-Old CDC architecture), CL-RKO-USB-003 (E3-Old descriptor locations), CONTRADICTION-USB-001 (base address error)
- **Contradiction Note:** Session used 0xB8007000 as USB base (from E1 analysis), later refuted by BSP ground truth (0xB1008000)
- **Tags:** usb, cdc, patch-strategy, risk-assessment, descriptors, firmware-modification
- **Created:** 2025-12-02
- **Evidence Tier:** E2 (implementation planning)
- **Status:** Strategy valid, but USB base address corrected in later analysis (CONTRADICTION-USB-001)

---

## Integration Notes

**E2-USB Evidence Type:** Strategic planning and implementation roadmaps that document:
1. Decision-making process for project goals
2. Risk assessment for binary patching
3. Implementation strategy evolution
4. Early analysis errors (later corrected)

**Relationship to Other Tiers:**
- **E1 Tier:** E2-USB-006 explains why CL-USB-004 trigger analysis was prioritized
- **E3-Old:** E2-USB-011 planning fed into CL-RKO-USB-002 and CL-RKO-USB-003 findings
- **E3-New:** Both sessions contain USB base address error (0xB8007000), corrected by CL-RKN-SOC-002 (0xB1008000)

**CONTRADICTION-USB-001 Impact:** E2-USB-011 documents early CDC planning using incorrect USB base address. Strategy remains valid, but register references need updating per CONTRADICTION-USB-001 resolution.

---

*Evidence file created: 2026-01-04*
*E2 Tier: Strategic planning and implementation roadmaps*
