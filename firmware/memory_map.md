# Document Status: to be verified

# Memory & MMIO Map

**SoC:** Nuvoton N32903U5DN (ARM926EJ-S)
**Endianness:** Little Endian

## Physical SDMemory Layout

| Range | Size | Description |
| :--- | :--- | :--- |
| `0x00000000` | 8 MB | **SDRAM (DDR)**. Stacked inside SIP. |
| `0x03000000` | - | **APP.bin Load Address**. (High memory, likely aliased or MMU mapped). |
| `0xB0000000` | - | **MMIO Peripheral Region** |
| `0xFF000000` | 8 KB | Internal SRAM |
| `0xFFFF0000` | 16 KB | Internal Boot ROM (IBR) |

## Peripheral Registers (APB/AHB)

| Base | Name | Verified Functions |
| :--- | :--- | :--- |
| `0xB0000000` | **GCR** | Global Control. `0x84`=GPBFUN (PinMux). `0x204`=Clk. |
| `0xB100D000` | **LCM** | Display Controller. Used by `0x230E04` for screen updates. |
| `0xB8000000` | **AIC** | Interrupt Controller. |
| `0xB8001000` | **GPIO** | Ports A-E. Offsets: `+0x00`=A, `+0x40`=B, etc. |
| `0xB8002000` | **TMR** | Timer/Watchdog. |
| `0xB8003000` | **UNK** | **Encoder Interface.** Used by `encoder_read` (`0x8f9a8`). |
| `0xB8007000` | **PWM** | Backlight Control (`0x5c1a0`). |
| `0xB800C000` | **SPI0** | Used as "Doorbell" for Display Commands. |
| `0xB800E000` | **ADC** | Voltage Monitor (`VADJ`, `VIN`) & Touchscreen. |

## Key RAM Structures

| Address (VA) | Description |
| :--- | :--- |
| `0x0037E820` | **Upgrade Filename Table.** Pointers to `3:/ZK-INKJET...` strings. |
| `0x003D3E00` | **Message Handler Table.** Dispatches UI events (Upgrade found, etc). |
