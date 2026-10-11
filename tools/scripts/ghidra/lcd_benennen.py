# Benennt die Display-Routinen (ST7789V ueber SPI0), belegt am Disassemblat am
# 2026-10-11 (CL-DISPLAY-REC-117). Nur Funktionen mit Standardnamen werden umbenannt;
# jede bekommt einen Plate-Kommentar mit dem Beleg. Idempotent.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType

Q = " (CL-DISPLAY-REC-117)"
TABELLE = [
    (0x000C7D90, "lcd_write_cmd",
     "GPE8 (REG_GPIOE_DOUT Bit 8) low, r0 nach REG_SPI0_TX0, REG_SPI0_CNTRL=0x45 (8 Bit, GO), warten, "
     "GPE8 high. GPE8 ist die D/C-Leitung: low = Befehl."),
    (0x000C7DD4, "lcd_write_data16",
     "r0 nach REG_SPI0_TX0, REG_SPI0_CNTRL=0x85 (16 Bit, GO), warten. D/C bleibt high: Daten, ein RGB565-Pixel."),
    (0x000C7D70, "lcd_gpd13_set",
     "r0!=0 setzt, r0==0 loescht REG_GPIOD_DOUT Bit 13. Zweimal je Fenster-/Initroutine aufgerufen -- "
     "vermutlich Chip-Select, nicht gemessen."),
    (0x0007577C, "lcd_set_window_write",
     "lcd_write_cmd 0x2A CASET, 0x2B RASET, 0x2C RAMWR mit Koordinaten als Daten."),
    (0x000751C0, "lcd_set_window_read",
     "lcd_write_cmd 0x2A CASET, 0x2B RASET, 0x2E RAMRD -- Fenster setzen und Pixel zuruecklesen."),
    (0x000750C0, "lcd_fill_rect",
     "CASET/RASET/RAMWR mit berechneten Koordinaten, dann eine Farbe wiederholt per lcd_write_data16."),
    (0x00074AB0, "lcd_blit",
     "CASET/RASET/RAMWR, dann Pixel aus dem Puffer per lcd_write_data16; verzweigt nach Pixelformat, "
     "u. a. 16 Bit und 32 Bit mit Alpha 0/0xFF/Mischung (0x112764, 0x112834). Ghidras Rumpf endet zu frueh, "
     "der Code laeuft bis 0x7506C."),
    (0x001150E0, "lcd_init",
     "ruft 0x117D3C und 0x1139D0, springt dann nach 0x7523C: ahb_clk_enable_and_reset, 0x11 SLPOUT, "
     "delay_ms(120), 0xB2 0xB7 0xBB 0xC3 0xC4 0xC6 0xD0 0xE0 0xE1 0x3A 0x36, 0x29 DISPON -- die ST7789V-Sequenz "
     "wie in BOOT.bin (CL-DISPLAY-REC-002/-113)."),
    (0x0009EE48, "delay_ms",
     "Schleife mit 1000 (0x3E8) je Einheit ueber Timer-Register; nach SLPOUT mit 120 aufgerufen, wie das "
     "ST7789-Datenblatt es verlangt."),
    (0x000C7C20, "ahb_clk_enable_and_reset",
     "setzt Bits 0x1000000|0x20 und 0x800 in REG_AHBCLK, pulst Bits 0x10000 und 0x8 in REG_AHBIPRST."),
    (0x00112D08, "lcd_clear_screen",
     "bl 0x115A0C(0,0), dann lcd_fill_rect(0,0, Breite=[g+8], Hoehe=[g+0xC], Farbe=[g+0x14]) aus der "
     "globalen Display-Struktur (Zeiger im Poolwort 0x112D3C)."),
    (0x00112D40, "lcd_fill_rect_bg",
     "lcd_fill_rect mit der Hintergrundfarbe [g+0x14]."),
    (0x00113E88, "lcd_fill_rect_fg",
     "lcd_fill_rect mit der Vordergrundfarbe [g+0x10]."),
    (0x00112D5C, "lcd_draw_image",
     "verzweigt nach der Ausrichtung [g+0x34] = 0/1/2 und ruft je Fall lcd_blit."),
]

fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
n_neu = n_schon = 0
fehler = []
for va, name, beleg in TABELLE:
    f = fm.getFunctionAt(toAddr(va))
    if f is None:
        fehler.append("0x%08X keine Funktion" % va)
        continue
    if f.getName() == name:
        n_schon += 1
    elif f.getSymbol().getSource() == SourceType.DEFAULT:
        println("   0x%08X  %-14s -> %s" % (va, f.getName(), name))
        f.setName(name, SourceType.USER_DEFINED)
        n_neu += 1
    else:
        fehler.append("0x%08X traegt schon %s, bleibt" % (va, f.getName()))
        continue
    lst.setComment(toAddr(va), CodeUnit.PLATE_COMMENT, name + ": " + beleg + Q)

println("umbenannt %d, schon richtig %d" % (n_neu, n_schon))
for x in fehler:
    println("   " + x)
