# Hardware Specification: ZK-DP20 / ZK-1696

**SoC:** Nuvoton N32903U5DN  
**Architecture:** ARM926EJ-S (ARMv5TEJ) @ 200 MHz  
**Memory:** 8MB Stacked DDR SDRAM (Internal to SIP)  
**Storage:** External MicroSD on PCB (Single slot, used for both Boot and Filesystem)

## The SoC: N32903U5DN
Confirmed via datasheet analysis and pinout verification.
*   **U5DN Variant:** Includes 8MB stacked DDR (verified via datasheet p.62).
*   **Non-OS BSP:** The firmware is a bare-metal loop, not Linux.
*   **Datasheet:** See `docs/vendor/N3290x_Design_Guide_A1.pdf` (local copy - online see [N3290x_Design_Guide_A1.pdf](http://file.whycan.com/files/members/3907/N3290x_Design_Guide_A1.pdf) and [N3290x_DataSheet_Revision_A6.2.pdf](https://www.nuvoton.com/resource-files/N3290x_DataSheet_Revision_A6.2.pdf).

## Peripheral Mapping

| Function | Controller Base | Notes |
| :--- | :--- | :--- |
| **GCR** | `0xB0000000` | Global Control (Pin Mux, Chip ID) |
| **GPIO** | `0xB8001000` | Ports A-E |
| **PWM** | `0xB8007000` | Backlight Control |
| **ADC** | `0xB800E000` | Voltage monitoring & Touchscreen |
| **Display** | `0xB100D000` | LCD Interface (ST7789V via SPI0) |
| **Doorbell** | `0xB800C000` | Custom communication block |

## Pinout & Constraints

For the full pinout, see [N32903U5DN_Pinout.md](N32903U5DN_Pinout.md).

**⚠️ Critical Constraints:**
1.  **UART0 is BLOCKED:** The standard console pins (GPA10/11) are physically wired to the Printhead Driver (IC2). Attaching a serial console here will corrupt print data or damage the head.
2.  **Debug Header:** The 4-pin header (GPB[2-5]) is electrically connected but **software disabled** (unconfigured in PinMux). This is the safest injection point for mods.
3.  **LCD Backlight:** Shares the JTAG TCK pin. Hardware debugging requires disabling the backlight.

## The Printhead Interface (HP45)
Driven by 6x **CM504B** Level Shifters (3.3V logic -> 12V head voltage).
*   **Address Lines:** 22 (HA0-HA21)
*   **Primitives:** 14 (HP0-HP13)
*   See `docs/findings/finding-0012.json` for exact mapping.
