# Hardware, assembly and battery

## Exact device

- Waveshare **ESP32-S3-Touch-AMOLED-1.75C**; owner's photo visibly shows Rev 1.1.
- ESP32-S3 rev 0.2 reported over USB; 32 MB flash and embedded 8 MB octal PSRAM.
- Round 466 × 466 CO5300 AMOLED and CST9217 touch.
- ES8311 speaker codec and ES7210 dual-microphone ADC; audio recorded/played at 16 kHz in the Muse audio path.
- AXP2101 power manager, 3.7 V battery connector and USB power.
- Top PWR/talk key is read through GPIO3 on this 1.75C. Bottom key is BOOT/GPIO0. Do not transfer pin assignments to the non-C board.
- Native USB JTAG/serial; the historical port was `/dev/cu.usbmodem101` but is not a permanent identifier.

The board also contains hardware such as an IMU, but the current installation does not demonstrate a motion-driven product feature. Hardware presence is not a claim of firmware integration.

References: [vendor documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.75C), [official vendor source](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.75C), and the pinned Muse `board_waveshare_s3_175c.c`.

## Battery connection and physical fit

Waveshare specifies a **single-cell 3.7 V lithium battery** on an **MX1.25 two-pin** battery connector, with charge/discharge support. Confirm cell specifications, connector polarity and charge-current compatibility rather than relying on plug shape. We did not read a legible battery capacity/rating label or verify polarity with a meter in this session.

The supplied photo showed a silver pouch battery, yellow terminal insulation and a white adhesive release liner marked 3M. Important distinctions:

- Leave yellow tape and the silver pouch intact. Yellow insulation is **not** the adhesive release liner.
- Only an identified release liner is peeled to expose mounting adhesive.
- Do not stick the pouch onto a chip, exposed contacts, sharp solder joints or screw hardware. A suitable flat case surface needs clearance and electrical separation.
- Power off and unplug USB before physical installation.
- Dry-fit before fixing it. The lid must close without squeezing/bending the pouch or pinching its wires. A closed lid alone does not prove safe clearance.
- Leaving the release liner on is acceptable only if the battery remains securely restrained without compression or abrasion. Loose retention and lid pressure are not substitutes for a suitable mount.

The owner reported closing the case tightly without peeling the liner. This is a **reported assembly state**, not an approved fit. If force was needed, reopen and check it. No claim is made that the photo established a safe position, cell health or polarity. The original HEIC/photo is kept only in the private local archive.

## Runtime remains unmeasured

The owner tentatively identified **500 mAh**. Confirm the printed capacity and safe charging specification. Conditional arithmetic with 80% usable capacity gives:

| Assumed average battery current | Calculated runtime for 500 mAh |
|---:|---:|
| 100 mA | 4 h |
| 200 mA | 2 h |
| 300 mA | 1 h 20 min |

These are examples, **not measured Arc current or predicted standby performance**. Wi-Fi conditions, voice use, display brightness, speaker output, codec duty cycle, regulator losses and battery condition affect runtime. USB-connected operation is not representative of battery sleep behavior.

Suggested usage record: confirmed cell capacity, start/end times, charging state, brightness, approximate live-call minutes, screen-off periods and any restarts/heat. No discharge endurance, charge-current, closed-case temperature or swelling test was carried out. Stop using a visibly swollen/damaged or abnormally hot battery.
