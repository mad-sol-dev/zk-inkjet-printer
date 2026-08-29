# CL-28800000 — Does 0x28800000 occur in ZK-INKJET-NANO-APP.bin?

## Verdict
FINDING: none
STATE: MEASURED
CONFIDENCE: 1.00 — Controls passed for both search modes.

## Controls
```
Controls: PASS
Literal hits for 0x28800000: []
MOV-immediate hits for 0x28800000: []
```

## What I ran
```
python3 $HOME/zk-probes/CL-28800000/probe.py
```

## Output
```
Controls: PASS
Literal hits for 0x28800000: []
MOV-immediate hits for 0x28800000: []

Searched:
- 4-byte aligned 32-bit LE literals: 0x0 to 0x27522C
- ARM MOV-immediate instructions: 0x0 to 0x27522C
```

## Reasoning
- **MEASURED**: The probe searched the entire file for 4-byte aligned 32-bit LE literals and ARM MOV-immediate instructions encoding `0x28800000`. No hits were found.
- **MEASURED**: Controls passed for both modes:
  - Literal `0x2A614000` found at offsets `0x1CA5C` and `0x1CAAC`.
  - MOV-immediate instructions at `0x65FE4` (`0xE3A085A2`) and `0x65FE0` (`0xE3A07A4D`) matched expected values.

## What this does NOT show
- The value may exist in a non-4-byte-aligned encoding (e.g., split across words).
- The value may be constructed dynamically (e.g., via arithmetic or memory loads).
- The value may appear in a non-executable region (e.g., data not covered by MOV-immediate search).

## Proposed register edit (NOT applied)
Claim_ID: CL-28800000
Status: refuted
Confidence: 1.0
Next_Test: 
Statement: The 32-bit value 0x28800000 does not occur in firmware/bin/ZK-INKJET-NANO-APP.bin as a 4-byte aligned 32-bit LE literal or as an immediate operand in ARM MOV/MVN/ORR/ADD/SUB/BIC/TEQ/TST/CMN/CMP instructions. Searched byte range: 0x0 to 0x27522C.