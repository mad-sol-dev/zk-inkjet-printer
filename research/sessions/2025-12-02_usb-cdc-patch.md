# Session: USB CDC Patch Planning (N32903 / W55FA93)

Date: 2024-12-02  
Context: Prepare CDC (Virtual COM) to replace MSC in `ZK-INKJET-NANO-APP.bin`. Chip: N32903 / W55FA93. UDC base: `0xB8007000`. Descriptor blob with product string at VA `0x00475140` (file offset ≈ `0x475140`), length 236 bytes.

## CDC Descriptor Template (FS)
- Tracer header:
  - Magic: `5A 4B 43 44` (“ZKCD”)
  - Version: `01 00 00 00`
  - Build: ASCII `CDC-PATCH-v001-20241202 00`
- Device descriptor (18B):
  ```
  12 01 00 02 02 00 00 40 16 04 12 50 00 03 01 02 00 01
  ```
  (VID 0x0416, PID 0x5012 placeholder; bDeviceClass 0x02 CDC, bMaxPacket0 64)
- Config block (0x43B, 2 interfaces: CDC control + data):
  ```
  09 02 43 00 02 01 00 C0 32
  09 04 00 00 01 02 02 01 00
  05 24 00 10 01
  05 24 01 00 01
  04 24 02 00
  05 24 06 00 01
  07 05 83 03 40 00 01      ; EP3 IN interrupt
  09 04 01 00 02 0A 00 00 00 ; Data IF
  07 05 81 02 40 00 00      ; EP1 IN bulk
  07 05 02 02 40 00 00      ; EP2 OUT bulk
  ```
- String descriptors: can reuse existing LangID/manufacturer/product or replace with short UTF-16 strings (fit within 236-byte budget; pad with 00s).
- Patch target: replace 236-byte blob at file offset ≈ `0x475140` with tracer + device + config + strings (pad to 236 bytes).

## UDC Base References (0xB8007000 literals)
Offsets in file where the base literal appears:
```
0x30ab8, 0x323cc, 0x46c28, 0x46ebc, 0x46f28, 0x5c3d8, 0x8b03c, 0xa3b08, 0xb4068, 0xb40fc
```
Findings:
- Helper at `0x46e48` uses `base+0x30`, `base+0x08`, waits on `base+0x38` — UDC reset/sync style.
- Other sites still need manual walk to find EP config writes (EPA_CFG/EPB_CFG/EPC_CFG) and control dispatcher.
- Function at `0x46c2c` is unrelated (string sanitizer).

## Outstanding Tasks
1) Disassemble functions containing base hits (esp. 0x8b03c, 0xa3b08, 0xb4068, 0xb40fc) to locate writes to `0xB8007000 + offsets` (STR/STRB). Log offset/value for EP configs (types, EP numbers, MPS, buffer start/end).
2) Locate control-request dispatcher: search for bRequest/bmRequestType switch (0x06, 0x09, 0x20/0x21/0x22) to hook CDC class requests.
3) Build final patch table:
   - [0x475140, 236, old_blob, new_blob_with_tracer, “Replace MSC string blob with CDC descriptors”]
   - EP config register changes (old/new values) once mapped.
   - Control handler hook for CDC class requests.
4) Keep PID distinct (e.g., 0x5012) to differentiate from MSC.

## Notes
- APP is loaded to 0x03000000 (identity-mapped MMU; >48 MB RAM assumed). Descriptor patch is data-only; code patch depends on available space near UDC init.
- CDC endpoints (plan): EP1 IN bulk, EP2 OUT bulk, EP3 IN interrupt, all MPS 64 (FS). EP0 unchanged.
- If dual-config needed (MSC + CDC), ensure UDC stack supports multiple configs; otherwise CDC replaces MSC. Rollback: restore original 236-byte blob.
