# 2026-10-18 -- Restarts without battery, the VADJ regulator, a diagnostic PIN

Not authoritative. Authoritative is `research/TRUTH.csv`.
Commits: `63dd232`, `f43c79c` (pushed to origin/master), plus this log.
Written by Claude (Opus 5.5); not yet reviewed by the maintainer.

## Starting point

Earlier that day the maintainer (@mad-sol-dev) had seen, with the printhead
flex and the cartridge disconnected and the board on USB power only: without
the battery, pressing the key in the edit menu, which normally opens the print
menu, hung the device, and opening the diagnostic menu restarted it. With the
battery both worked. Both had been seen after USB boots. Three hypotheses were
open: the firmware reacting to an implausible battery reading, the inrush of
the printhead rail VADJ pulling the supply down, a hang ending in the
watchdog reset.

The goal was to find what the two menu entries do that depends on the
battery, and to propose one device test at a time.

## What I did

I started by reading the code. The status line reads the battery voltage
every 10 s and has an undervoltage shutdown. That shutdown needs the charge
state -1, which means no VBUS, so it cannot fire with the cable in.

Both menu entries share exactly one power-related step: slot +0xC of the
print head ops table, 0x10C06C, called with 9.0 V from the settings. Reading
it gave a software regulator: PWM2's comparator CMR2 is stepped against ADC
channel 3, the value the diagnostic menu calls VADJ, and GPD3 switches it on.
Outside these two screens and a hidden calibration the setpoint stays 0. That
made the VADJ inrush my favourite, and I said so, too early.

While reading the diagnostic event handlers I found a PIN dialog in front of
three hidden actions. The maintainer had never entered a PIN; the 'MAGIC'
value known from the screen is not it.

From there we tested on the device, with live RAM boots over USB
(`tools/scripts/live_image.py`, `../n329-usbboot`), so nothing was written to
the card.

## Device tests

Facts, as recorded in CL-HARDWARE-REC-118. Battery out throughout; "card"
means the unmodified firmware booted from the card, which is what runs after
every restart.

| Firmware | Entry | Result |
|---|---|---|
| not recorded | print menu, short cable, then a 20 Ah power bank | restart, no change |
| live, vadj_set removed | print menu | restart |
| (card after that restart, presumably) | diagnostic menu | ok: VIN 4.67 V, charge state 1, VADJ 9.09 V |
| live, vadj_set removed, return at print loop head | print menu | restart on the first entry |
| card | print menu, 3 entries | I X I (I = ok, X = restart) |
| live, vadj_set removed, row label patched to 'VOFF' | diagnostic menu first | restart |
| card | diagnostic menu | ok: VIN 4.67 V in red, charge state 1, VADJ 9.09 V steady |
| card | print menu, 8 entries | X I X I X X X I |

The screen of the new menu shows for half a second or less, then goes black
and the device boots again. A converter whine is audible without the battery.
The menu settings were key click on, print tone on, sync mode encoder, start
signal key, print times 1000, Blink 0 s.

## What did not hold

**The VADJ call as trigger.** After the first patched run the diagnostic menu
worked, and I took that as support. In that run the print entry probably came
first and restarted the device, so the diagnostic entry most likely ran on
card firmware. The repeat with a visible marker ('VOFF' instead of 'VADJ' in
the diagnostic row) restarted on the first entry.

**USB boot versus card boot.** For a while all crashes on first entry came from
USB boots, and the original observation had been made after USB boots too.
Eight entries from a card boot, five restarts, ended that.

**The puzzle of 9.09 V without the VADJ call.** It came from reading the card
firmware as if it were the patch. 9.09 V lies in the regulator's 9.0..9.1 V
band.

What is left, as a reading (O1): an electrical reset of the USB-only supply
path inside the device, during the load step of a screen change. The code
excludes the watchdog (22.4 s), CPU exceptions (the abort vectors are `b .`),
the four firmware restart paths (all beep or wait first) and the undervoltage
shutdown. The maintainer parked the question; tests that open these menus run
with the battery.

## Results in the register

- CL-FIRMWARE-REC-131: PWM2 (CMR2) is closed-loop controlled against ADC
  channel 3 ('VADJ'); vadj_set 0x10C06C, start duty 0xB744C by VIN range, GPD3
  as enable. This withdraws the backlight reading of PWM2 in
  CL-HARDWARE-REC-115.
- CL-FIRMWARE-REC-132: the diagnostic menu asks for the PIN 86075527202606
  before three actions. One is a VADJ sweep that, by the firmware's regulator
  model, starts at the highest voltage, stops below 7 V and writes `3:\inkjet-lite-vadj-sample.csv` to the card.
- CL-FIRMWARE-REC-124: the fast restart 0x8A730 has four callers, not two;
  the two missed ones are the power-off paths, which release GPB6 first.
  Rewritten in English.
- CL-FIRMWARE-REC-127: the 0x10C06C part of its test is answered; the I2C
  header words remain.
- CL-HARDWARE-REC-118: the restarts without battery, parked, with a lab supply
  on the battery terminals as the next test.

## Device and artefacts

Nothing was written to the card. The blocks were built into `build/live/`
(gitignored); the patch words are in the evidence of CL-HARDWARE-REC-118. A
restart ends a live RAM boot, because BOOT.bin then reads APP from the card
again.

## Open threads

- CL-HARDWARE-REC-118, parked: lab supply on the battery terminals instead of
  the battery, ten entries per menu, current noted.
- CL-USB-REC-128 still says that 0x8A730 has two callers. Not touched, because
  the cell is far over the size limit.
- After the PIN, actions 0x165 (with 'SD Card', '0:/user/font'; the maintainer
  knows a menu option for user fonts) and 0x164 are not read. 0x166 writes to
  the card. Neither should be triggered on the original card.

## Mistakes of this session

**A result from one trial, without checking which firmware ran.** After a
restart the card firmware runs, and nothing on the screen said so. The 'VOFF'
marker should have been in the first patched block. For live RAM tests: always
patch a visible marker.

**"Password" before reading.** In my first answer I mentioned a "diagnostic
password" that I had only inferred from the decompiled code. The maintainer
asked, and only then did I read it.

**A control that was no news.** My first test proposal repeated what the
maintainer had been doing all along. What actually helped was counting entries
from the card boot.

**A false GPIO hit from my own tool.** My quick function-boundary heuristic ran
one function into the next and reported a GPIO access in the label rendering.
I caught it before drawing a conclusion.
