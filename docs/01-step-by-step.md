# Step-by-step: a Mac and Xiaozhi board to Muse live voice

This guide recreates the **final working setup**, with references to the unsuccessful attempts. The board must be the **1.75C AMOLED**, not the 1.75 without C, 1.85C LCD, or default ESP32-C5. Building is reversible; writing firmware needs a separate deliberate decision.

## 1. Establish basic USB connectivity

1. Use a USB-C data cable and connect Arc directly to the Mac.
2. Check the board label. The owner's photo shows `Touch-AMOLED-1.75C Rev1.1`.
3. List available ports:

   ```sh
   ls /dev/cu.usb*
   ```

   This device appeared as `/dev/cu.usbmodem101`, a native USB JTAG/serial device. Port names can change. Do not assume a matching port identifies the board model.

4. Close browser flashers and serial monitors before opening the port elsewhere. Use one active reader/writer at a time.
5. If necessary, install Apple Command Line Tools (`xcode-select --install`) and Homebrew from its official site. This session already had both; their original installation was not observed.
6. Install Python 3.13, then use an isolated environment:

   ```sh
   brew install python@3.13
   /opt/homebrew/bin/python3.13 -m venv .local/esptool-env
   .local/esptool-env/bin/python -m pip install esptool==5.6.0
   export ARC_PORT=/dev/cu.usbmodem101
   .local/esptool-env/bin/python -m esptool --chip esp32s3 --port "$ARC_PORT" flash-id
   .local/esptool-env/bin/python -m esptool --chip esp32s3 --port "$ARC_PORT" get-security-info
   ```

   On Intel Macs the Homebrew path differs. Substitute the actual Python 3.13 path. Expected on this board: ESP32-S3 rev 0.2, **32 MB flash**, embedded **8 MB PSRAM**, Secure Boot and flash encryption disabled. These read-only queries reset the board briefly.

## 2. Back up the complete working firmware

Do this **before any erase/write**. A 16 MiB file is incomplete for this 32 MiB unit.

```sh
mkdir -p .local/recovery
chmod 700 .local .local/recovery
umask 077
.local/esptool-env/bin/python -m esptool --chip esp32s3 --port "$ARC_PORT" \
  --baud 460800 read-flash 0x0 0x2000000 .local/recovery/arc-xiaozhi-full-32mb.bin
shasum -a 256 .local/recovery/arc-xiaozhi-full-32mb.bin
.local/esptool-env/bin/python -m esptool --chip esp32s3 --port "$ARC_PORT" \
  verify-flash 0x0 .local/recovery/arc-xiaozhi-full-32mb.bin
```

Use a new filename for a new capture; never overwrite the only known-good backup. The historical backup's hashes are in [recovery evidence](../evidence/recovery-validation.json). A fresh backup of another board/state will have a different hash. `verify-flash` compares without writing firmware. Treat the dump as secret: it contains configuration and potentially credentials.

## 3. Preserve official factory recovery separately

Get `ESP32-S3-Touch-AMOLED-1.75C-FactoryOnly-260114.bin` from [Waveshare release v1.0.1](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.75C/releases/tag/v1.0.1). The verified asset is **33,488,896 bytes**, SHA-256:

```text
46e65fb708f325f6830d6f14ecbba3d357dbdab6a939e13fdf2206e147c063d2
```

The factory demo is different from the saved Xiaozhi setup. Keep both. Factory file size need not equal the full physical flash capacity. See [recovery](05-backup-and-recovery.md).

## 4. Install the pinned Muse toolchain

```sh
brew install cmake ninja dfu-util python@3.13 mbedtls pkgconf
python3 scripts/bootstrap.py
```

The helper clones the pinned official sources into ignored `.local/`, recursively initializes ESP-IDF submodules, and installs only the ESP32-S3 toolchain there. It does not modify Arc. Run it with Python 3.13 on PATH:

```sh
export PATH="$(brew --prefix python@3.13)/libexec/bin:$PATH"
python3 scripts/bootstrap.py
```

ESP-IDF **v6.0.3** is the SDK's supported version at the recorded commit. Do not substitute an arbitrary IDF release.

## 5. Supply the Muse SDK token privately

Create a local file containing your token from Muse Gadgets > Account > SDK tokens. Do not put the token in a command argument or commit it. Its real path is recorded only in the ignored local inventory.

```sh
export ARC_SDK_TOKEN_FILE=/absolute/path/to/your/private-token-file
python3 scripts/build.py
```

The helper reads the token without printing it and writes it to the ignored, private generated `sdkconfig`. The resulting firmware **also contains the token**, so binaries stay out of Git even in a private repository.

## 6. Confirm the exact build

The build combines the official defaults, Muse overlay, exact Waveshare 1.75C overlay, and [Arc live overlay](../configs/sdkconfig.arc-live). It must select:

```ini
CONFIG_IDF_TARGET="esp32s3"
CONFIG_MUSE_BOARD_WAVESHARE_S3_175C=y
CONFIG_ESPTOOLPY_FLASHSIZE="32MB"
CONFIG_SPIRAM_MODE_OCT=y
CONFIG_MUSE_REALTIME_VOICE=y
CONFIG_MUSE_STATIC_BUFFERS_IN_PSRAM=y
```

Confirm the image fits its 4 MiB app slot, Secure Boot/flash encryption remain disabled, and the image checksum/hash is valid. The helper performs these checks and creates a local artifact manifest. Byte-for-byte equality is not promised across new timestamps, machines, and regenerated build metadata; the historical installed image hash is preserved separately.

## 7. Decide whether this is a first migration or a Muse upgrade

**Upgrading an already paired Muse device:** preserve NVS. The included upgrade helper backs up NVS plus OTA state before writing and never issues an erase command:

```sh
python3 scripts/flash.py --port "$ARC_PORT"
```

That prints a plan only. A real write requires the explicit flags documented by `--help`. Verify the exact hardware before confirming. Do not use this helper for an uninitialized Xiaozhi-to-Muse migration.

**First Xiaozhi-to-Muse migration:** the partition layouts differ. Only after a verified full backup and explicit write approval, initialize Muse's new NVS region and write the split image set. Run from the generated build directory with IDF's Python environment:

```sh
# DESTRUCTIVE: first migration only, after explicit confirmation.
# Use the currently detected port and your actual local build path.
python -m esptool --chip esp32s3 --port "$ARC_PORT" erase-region 0x11000 0xc000
python -m esptool --chip esp32s3 --port "$ARC_PORT" --baud 460800 write-flash @flash_args
```

Do **not** run that erase on a paired Muse upgrade. Do not flash the app alone at address 0. Flash addresses are bootloader `0x0`, partition table `0x10000`, OTA data `0x1d000`, app `0x20000`.

## 8. Pair Muse and configure Wi-Fi

1. In Muse, enable Settings > Devices > Developer mode if required by the app.
2. Add the gadget matching the name on Arc's screen. Names/IDs are device-specific.
3. Confirm pairing with the physical button when requested.
4. Select an available **2.4 GHz** network and enter its password **in the app**.
5. Complete the entire account-pairing flow. Device-side Wi-Fi setup alone does not complete Muse account pairing.

Our router was an eero Pro 7. Temporarily pausing 5/6 GHz did not fix the problem by itself, and 2.4 GHz encryption was already Standard/WPA2. A guest-network attempt also initially appeared to fail. Later, configuring Wi-Fi directly on the Waveshare produced an actual IP connection; finishing the app's setup afterward completed pairing. The record does **not** establish that guest Wi-Fi, a specific eero setting, or one change alone caused success. See [the troubleshooting sequence](03-troubleshooting.md).

## 9. Validate voice with the correct gesture

1. Confirm Arc is awake and Muse reports connected.
2. **Quickly click and release the top PWR/talk button**, then speak hands-free when the live-call screen appears. The source distinguishes taps shorter than roughly 0.3 seconds from holds; capture-tail/debounce timing can reduce the practical margin.
3. Click again to end. Don't hold the button throughout your speech unless you want a voice note.
4. Verify audible speech, not just text captions or microphone tones.

If a short click only wakes the display, click again once awake. A logged 2.6-second press was correctly treated as a voice note. A controlled 80 ms press/release started a live call and proved spoken playback worked. Do not leave a call open unintentionally: firmware also applies a 45-second idle limit and a 15-minute maximum.

## 10. Try normal use and preserve changes

Use [daily controls](02-daily-use.md), record battery runtime, and consult [troubleshooting](03-troubleshooting.md) for regressions. Keep private backups separately. Rebuilds alone do not write firmware; obtain explicit confirmation again for future hardware writes.
