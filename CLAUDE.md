# CLAUDE.md

This file provides guidance to Claude (claude.ai) when working with this repository.

## Project Overview

Reverse engineering project for ZK-INKJET handheld printer firmware. Goal: Implement USB-CDC (Communication Device Class) for automatic lithium cell labeling. Hardware: Nuvoton N32903U5DN SoC (ARM926EJ-S) with mixed ARM/Thumb firmware.

**Key Characteristics:**
- Ghidra-based binary analysis with MCP integration
- Structured knowledge base (RE-KB) for findings documentation
- BSP headers and vendor datasheets as ground truth
- Fact-based analysis over speculation

**Current Focus:** Mapping USB stack architecture, MMIO register definitions, and firmware update mechanisms.

---

## Repository Structure

```
firmware/                    # Firmware binaries and resources
├── bin/ZK-INKJET-NANO-APP.bin  # Main application firmware (2.5MB)
├── bin/ZK-INKJET-NANO-BOOT.bin # Bootloader
├── ZK-INKJET-UI-QVGA.bin     # Start/Stop screen graphics
├── ZK-INKJET-RES-HW.zkml     # Handwriting resource container
├── ZK-INKJET-GUI-RES.zkml   # Font resource (Leelawadee UI)
├── image/sdcard.work.img    # SD card dump (1:1 raw)
├── memory_map.md            # Memory layout documentation
├── update_system.md         # Update system analysis
└── update_system.md         # Update system analysis

research/                    # Analysis outputs and documentation
├── findings/                # Structured findings + data
│   ├── .re_kb/              # RE knowledge base (MCP integration)
│   └── n32903_registers.json  # MMIO register map (1544 entries)
├── sessions/                # Chronological research logs
└── analysis/                # Processed outputs
    ├── decoded_ui.png       # Decoded UI graphics (with artifacts)
    ├── strings_report.md    # String extraction analysis
    └── upgrade_orchestrator_*.{json,txt}

tools/                       # Analysis tooling
├── scripts/                 # Python analysis scripts
├── legacy/                  # Archived/superseded tools
└── mcp_bridge/              # MCP server integrations

hardware/                    # Hardware documentation
├── N32903U5DN_Pinout.md     # SoC pinout mapping
├── README.md                # Hardware overview
└── images/                  # PCB photos, schematics

vendor/                      # External reference material (gitignored)
├── datasheets/              # N3290x Design Guide, etc.
└── bsp/                     # N32901-3 NonOS BSP headers
    └── N32901-3_NonOS_BSP/

ghidra_projects/             # Ghidra analysis projects
└── zk-inkjet/               # Current project
    └── ZK-INKJET-NANO-APP.bin/

mcp/                         # MCP server configurations
├── aiderdesk.json.example
└── codex.toml.example
```

---

## MCP Integration

This repository uses **Model Context Protocol (MCP)** servers for AI-assisted analysis:

### **1. GhidraMCPd** (Ghidra Bridge)
**URL:** http://127.0.0.1:8099/sse

**Primary Tools:**
- `project_overview` - List available programs in Ghidra project
- `select_program` - Switch active program by domain_file_id
- `get_current_program` - Check which program is active
- `search_strings` - Find strings with pagination
- `search_functions` - Find functions by name pattern
- `search_scalars` - Find scalar values with context
- `disassemble_at` - Disassemble at address
- `disassemble_batch` - Batch disassembly
- `read_bytes` / `read_words` - Memory reads
- `collect` - **Batch multiple queries in one call**

**Example Workflow:**
```python
# 1. Select program
ghidra.select_program(domain_file_id="/ZK-INKJET-NANO-APP.bin")

# 2. Search for USB strings
ghidra.search_strings(query="USB", limit=50)

# 3. Find scalar references with context
ghidra.search_scalars_with_context(value="0xB1008000", context_lines=4)

# 4. Batch query
ghidra.collect(queries=[
    {"id": "usb_strings", "op": "search_strings", "params": {"query": "USB"}},
    {"id": "usb_base", "op": "search_scalars", "params": {"value": "0xB1008000"}}
])
```

### **2. RE-KB MCP** (Knowledge Base)
**URL:** http://127.0.0.1:8000/sse  
**Path:** `research/findings/.re_kb/`

**CRITICAL:** Must activate project before use:
```bash
bash research/findings/.re_kb/select_this_project.sh
```

**Primary Tools:**
- `get_finding_template` - Show complete finding structure
- `list_finding_enums` - Valid values for type/status/severity/evidence
- `create_finding` - Create new finding (see template)
- `update_finding` - Partial update by ID
- `attach_evidence` - Add evidence to finding
- `list_findings` - Query with filters
- `get_finding` - Load complete finding by ID

**Finding Types:**
- `bug` - Code defects
- `vuln` - Security vulnerabilities  
- `behavior` - System behaviors (most common)
- `hypothesis` - Unverified theories (requires confidence 0.0-1.0)
- `todo` - Action items

**Evidence Types:**
- `ghidra` - Ghidra analysis (function_address, decompiler_snippet, etc.)
- `pdf` - Vendor documentation (document_id, page)
- `log` - Log files (log_file, line_number)
- `test` - Test results (test_id, result)
- `other` - General observations (description only)

**Example Finding Creation:**
```python
# Get template first
re_kb.get_finding_template()

# Create verified behavior
re_kb.create_finding({
    "project_id": "zk-inkjet-printer",
    "type": "behavior",
    "status": "verified",
    "title": "USB Device Controller Base Address",
    "summary": "USB controller registers located at 0xB1008000",
    "evidence": [{
        "source_type": "ghidra",
        "function_address": "0x00217DD0",
        "description": "Function accesses USB_BA register"
    }],
    "tags": ["usb", "mmio", "hardware"],
    "component": "usb-stack",
    "confidence": 1.0
})
```

**Query Examples:**
```python
# List all USB findings
re_kb.list_findings(filters={"tag": "usb"})

# List in-progress work
re_kb.list_findings(filters={"status": "in_progress"})

# High-confidence hypotheses
re_kb.list_findings(filters={"type": "hypothesis", "min_confidence": 0.8})
```

### **3. PDF Reader MCP** (Vendor Documentation)
**Type:** stdio  
**CWD:** `vendor/datasheets/`

**Primary Tools:**
- `pdf_info` - Get metadata (pages, TOC, stats)
- `pdf_read` - Extract text from pages
- `pdf_search` - Search for patterns
- `pdf_vision` - Analyze diagrams/charts (Mistral Vision)
- `pdf_ocr` - OCR text from images

**Key Documents:**
- `N3290x_Design_Guide_A1.pdf` (897 pages)
  - System Memory Map: pages 47-49
  - GPIO Controller: pages 645-668
  - UART Controller: pages 750-779
  - SPI Controller: pages 780-811
  - Timer Controller: pages 669-680
  - Interrupt Controller (AIC): pages 624-644

**Example Usage:**
```python
# Read GPIO documentation
pdf_reader.pdf_read(sources=[{
    "path": "N3290x_Design_Guide_A1.pdf",
    "pages": "645-668"
}])

# Search for register name
pdf_reader.pdf_search(
    sources=[{"path": "N3290x_Design_Guide_A1.pdf"}],
    query="USB_PHY_CTRL",
    max_hits=10
)
```

---

## Firmware Analysis Workflow

### **Phase 1: Initial Discovery**

1. **Load program in Ghidra**
   ```python
   ghidra.project_overview()
   ghidra.select_program(domain_file_id="/ZK-INKJET-NANO-APP.bin")
   ```

2. **String reconnaissance**
   ```python
   ghidra.search_strings(query="USB", limit=100)
   ghidra.search_strings(query="error", limit=50)
   ```

3. **Hardware register scanning**
   ```python
   # USB controller base
   ghidra.search_scalars_with_context(value="0xB1008000", context_lines=5)
   
   # GPIO base
   ghidra.search_scalars_with_context(value="0xB8001000", context_lines=5)
   ```

### **Phase 2: Function Analysis**

1. **Search for candidate functions**
   ```python
   ghidra.search_functions(query="usb", limit=20, context_lines=3)
   ```

2. **Analyze function disassembly**
   ```python
   ghidra.disassemble_at(address="0x00217DD0", count=50)
   ```

3. **Batch analysis**
   ```python
   ghidra.collect(queries=[
       {"id": "func1", "op": "disassemble_at", "params": {"address": "0x217DD0"}},
       {"id": "func2", "op": "disassemble_at", "params": {"address": "0x218000"}},
   ])
   ```

### **Phase 3: Documentation**

1. **Create finding for discovery**
   ```python
   re_kb.create_finding({
       "project_id": "zk-inkjet-printer",
       "type": "behavior",
       "title": "USB Initialization Sequence",
       "summary": "Function at 0x217DD0 initializes USB controller...",
       "evidence": [{"source_type": "ghidra", "function_address": "0x217DD0"}],
       "status": "in_progress",
       "tags": ["usb", "initialization"]
   })
   ```

2. **Document session**
   - Create markdown in `research/sessions/YYYY-MM-DD_topic.md`
   - Reference finding IDs
   - Link Codex agent logs

### **Phase 4: Cross-Reference with Vendor Docs**

1. **Look up register details**
   ```python
   pdf_reader.pdf_read(sources=[{
       "path": "N3290x_Design_Guide_A1.pdf",
       "pages": "USB chapter pages"
   }])
   ```

2. **Update finding with vendor evidence**
   ```python
   re_kb.attach_evidence(
       finding_id="finding-0003",
       evidence={
           "source_type": "pdf",
           "document_id": "N3290x_Design_Guide",
           "page": 456,
           "description": "USB_PHY_CTRL register confirmed at offset +0x04"
       }
   )
   ```

---

## Key Conventions

### **Memory Addresses**

- **Virtual Addresses (VA):** Firmware loaded at 0x00200000
  - Format: `VA 0x0020C798 (file+0xC798)`
  - Calculation: `VA = 0x200000 + file_offset`

- **MMIO Addresses:** Hardware registers in 0xB0000000-0xBFFFFFFF range
  - Format: `MMIO 0xB1008000 (USB_BA)`
  - Always label explicitly as MMIO

### **ARM/Thumb Mode**

- **ARM Region:** 0x00200000-0x0020FFFF (32-bit instructions)
- **Thumb Region:** 0x00210000-0x0021FFFF (16-bit instructions)
- **Mixed Total:** ~18% Thumb, ~82% ARM
- Ghidra correctly handles both modes (verified 2025-12-27)

### **File Naming**

- Session logs: `YYYY-MM-DD_topic-description.md`
- Findings: Auto-generated `finding-NNNN.json`
- Analysis outputs: Descriptive names in `research/analysis/`

---

## Common Tasks

### **Search for Hardware Usage**

```python
# Find all references to USB controller
ghidra.search_scalars(value="0xB1008000", limit=50)

# Find GPIO writes
ghidra.search_scalars(value="0xB8001000", limit=50)

# Search with context (recommended)
ghidra.search_scalars_with_context(
    value="0xB1008000",
    context_lines=4,
    limit=25
)
```

### **Analyze Function Call Graph**

```python
# Find function references
ghidra.search_xrefs_to(address="0x00217DD0", query="", limit=50)

# Get caller disassembly
ghidra.disassemble_batch(addresses=[
    "0x002100c8",
    "0x002101ca",
    "0x002101f4"
], count=20)
```

### **Document New Discovery**

```python
# 1. Check if similar finding exists
re_kb.list_findings(filters={"tag": "your-tag"})

# 2. Create new finding
re_kb.create_finding({
    "project_id": "zk-inkjet-printer",
    "type": "behavior",
    "status": "in_progress",
    "title": "Your Discovery",
    "summary": "Brief description...",
    "evidence": [...],
    "next_steps": ["Step 1", "Step 2"],
    "tags": ["relevant", "tags"]
})

# 3. Create session log in research/sessions/
```

### **Update Existing Finding**

```python
# Update status after verification
re_kb.update_finding(
    id="finding-0002",
    patch={
        "status": "verified",
        "next_steps": [],
        "confidence": 1.0
    }
)

# Add new evidence
re_kb.attach_evidence(
    finding_id="finding-0002",
    evidence={
        "source_type": "ghidra",
        "function_address": "0x00218000",
        "description": "Additional USB init code"
    }
)
```

---

## Using Codex Agents

This repository uses **Codex (GPT-5.1)** for deep technical analysis via `spawn_agent`:

### **When to Use Codex**

✅ **Use Codex for:**
- Complex Ghidra analysis (function decompilation, call graphs)
- BSP header parsing
- Multi-step technical investigations
- Deep-dive on specific subsystems

❌ **Don't use Codex for:**
- Quick queries (use Ghidra MCP directly)
- RE-KB operations (use create_finding)
- Simple file operations (use desktop-commander)

### **Codex Best Practices**

**Task Structure:**
```python
spawn_agent(prompt="""
TASK: [Clear objective]

CONTEXT:
- [Relevant background]
- [What's already known]

INSTRUCTIONS:
1. [Step-by-step process]
2. [Specific constraints]
3. [Output format]

STOP CONDITION: [When to stop]
""", reasoning_effort="medium")
```

**Effort Levels:**
- `low` - Simple tasks (< 1 min)
- `medium` - Most analyses (2-5 min) **← Default**
- `high` - Complex investigations (5-15 min)
- `xhigh` - Very deep analysis (15+ min)

**Monitor Progress:**
```bash
# Check agent status
ls -lth ~/.cache/codex-as-mcp/logs/*.last_message.md | head -5

# Read latest completion
cat ~/.cache/codex-as-mcp/logs/codex_agent_*.last_message.md
```

**Agent Output Locations:**
- Logs: `~/.cache/codex-as-mcp/logs/`
- Work directory: `$HOME/workspace/zk-inkjet-printer`

---

## Critical Rules

### **RE-KB Club Rule #1**
**NEVER write files directly to `.re_kb/` directory!**

❌ **Wrong:**
```python
# Don't do this!
write_file(".re_kb/my_data.json", content)
```

✅ **Correct:**
```python
# Use create_finding API
re_kb.create_finding({...})

# Or save to research/findings/
write_file("research/findings/my_data.json", content)
```

### **RE-KB Status Rules**

- **Status "verified"** → `next_steps` must be empty `[]`
- **Status "in_progress"** → Can have `next_steps`
- **Type "hypothesis"** → Requires `confidence` field (0.0-1.0)
- **All findings** → Must have `project_id: "zk-inkjet-printer"`

### **Ghidra Access Rules**

- **Never access Ghidra when Codex is working with it**
  - Parallel access causes LOADING state conflicts
  - Let Codex handle Ghidra operations exclusively
  - Wait for agent completion before manual queries

- **If Ghidra hangs in LOADING state**
  - Ask user to restart Ghidra immediately
  - Don't attempt workarounds

### **Vendor Documentation**

- **BSP headers = Ground Truth** for N32903U5DN
  - Prefer BSP over generic Design Guide
  - BSP was compiled for this exact chip variant

- **Design Guide = Reference** for concepts
  - Use for understanding peripheral theory
  - Cross-reference with BSP for exact addresses

---

## Project Context

### **Current State (2025-12-27)**

**Completed:**
- ✅ ARM/Thumb mixed-mode verified
- ✅ Ghidra auto-analysis optimized (34k → 1.2k functions)
- ✅ MMIO register map extracted (1544 registers)
- ✅ USB base address confirmed: 0xB1008000
- ✅ BSP structs imported into Ghidra (143 structs, 79 enums)

**In Progress:**
- 🔄 MMIO register map import to Ghidra
- 🔄 USB function identification
- 🔄 Hardware register usage analysis

**Next Steps:**
1. Import n32903_registers.json into Ghidra memory map
2. Create C structs for USB/GPIO/ADC peripherals
3. Identify USB interrupt handlers
4. Map USB-CDC implementation points

### **Key Findings**

- **finding-0001:** ARM/Thumb Mixed-Mode confirmed
- **finding-0002:** N32903 MMIO Register Map extracted

See `research/findings/.re_kb/findings/` for complete findings.

### **Recent Sessions**

See `research/sessions/` for chronological logs:
- `2025-12-27_arm-thumb-analysis-mmio-extraction.md`

### **Old Repository**

Archived at: `$HOME/workspace/zk-inkjet-printer_old`
- Contains legacy data/ structure
- Reference for migration

---

## Important Notes

**Goal:** Implement USB-CDC for automatic lithium cell labeling

**Approach:**
- Evidence-based analysis (no speculation)
- BSP headers as ground truth
- Systematic hardware register mapping
- Structured findings in RE-KB

**Tools:**
- Ghidra 11.4.2 for binary analysis
- MCP servers for integration
- Codex (GPT-5.1) for deep analysis
- Claude (Sonnet 4.5) for orchestration

**Philosophy:**
- Document everything
- Verify before marking "verified"
- Session logs for traceability
- Findings over raw notes

---

*Updated: 2025-12-27 by Claude Sonnet 4.5*
