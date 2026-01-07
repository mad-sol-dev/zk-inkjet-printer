# RE KB Project: zk-inkjet-printer

This directory contains a structured reverse engineering knowledge base using the RE KB workflow.

## Quick Start

### 1. Activate This Project

Before using RE KB MCP tools, activate this project:

```bash
bash .re_kb/select_this_project.sh
```

Or using the CLI:

```bash
rekb select --root .
```

### 2. Create Your First Finding

Use the RE KB MCP tools to create findings. Here's a minimal example:

```json
{
  "project_id": "zk-inkjet-printer",
  "type": "behavior",
  "status": "verified",
  "title": "Example Finding",
  "summary": "A concise description of what was discovered",
  "tags": ["hardware", "soc"],
  "evidence": [{
    "source_type": "other",
    "description": "How this was verified"
  }]
}
```

**TIP**: Call `get_finding_template` MCP tool to get a complete example with all fields!

## Finding Types

- `bug` - Software defect or error
- `vuln` - Security vulnerability
- `behavior` - Observed system behavior or characteristic
- `hypothesis` - Theory requiring further investigation
- `todo` - Task or follow-up action needed

## Finding Statuses

- `open` - Newly discovered, not yet investigated
- `in_progress` - Currently being investigated
- `verified` - Confirmed and documented
- `closed` - Investigation complete or no longer relevant

## Evidence Types

### Ghidra Evidence

Reference Ghidra analysis results:

```json
{
  "source_type": "ghidra",
  "domain_file_id": "/firmware.gpr",
  "function_address": "0x8001234",
  "function_name": "encrypt_data",
  "description": "Function XORs input with 0x42",
  "decompiler_snippet": "return input ^ 0x42;"
}
```

### PDF Evidence

Reference documentation pages:

```json
{
  "source_type": "pdf",
  "document_id": "datasheet-v2.1",
  "page": 42,
  "description": "Register definition matches observed behavior"
}
```

### Other Evidence Types

- `log` - Log file references (with `log_file`, `line_number`)
- `test` - Test file references
- `other` - Any other evidence type

## Available MCP Tools

### Discovery Tools

- **`get_finding_template`** - Get a complete example finding structure
- **`list_finding_enums`** - List all valid enum values (types, statuses, evidence types)

### Core Tools

- **`create_finding`** - Create a new finding
- **`update_finding`** - Update an existing finding
- **`attach_evidence`** - Add evidence to a finding
- **`get_finding`** - Retrieve a complete finding by ID
- **`list_findings`** - List findings with optional filters
- **`rebuild_index`** - Regenerate index.json (rarely needed)

### Usage Examples

**List all verified findings:**

```json
{ "status": "verified" }
```

**List hardware-related behaviors:**

```json
{ "type": "behavior", "tag": "hardware" }
```

**Update finding status:**

```json
{
  "status": "verified",
  "raw_note": "Confirmed via hardware testing on 2025-01-15"
}
```

## Best Practices

1. **Use `summary` for concise descriptions** (max 2048 chars)
2. **Use `raw_note` for detailed analysis** (max 32KB) - dump raw thoughts here
3. **Tag consistently** - use lowercase, hyphen-separated tags
4. **Add evidence as you go** - use `attach_evidence` to build up proof
5. **Update status** - track your investigation progress
6. **Don't edit index.json manually** - it's auto-generated

## File Structure

```
.re_kb/
  README.md              # This file
  project.json           # Project metadata
  index.json             # Auto-generated finding index (DON'T EDIT)
  select_this_project.sh # Project activation script
  findings/
    finding-0001.json    # Individual findings
    finding-0002.json
  schema/                # JSON schemas for validation (optional)
    finding.schema.json
    index.schema.json
```

## Need Help?

- Call `get_finding_template` for a complete example
- Call `list_finding_enums` for valid field values
- Check tool descriptions for detailed parameter info
- See [RE KB Workflow Docs](../../docs/re_kb_workflow.md)
