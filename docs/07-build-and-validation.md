# Build and validation record

## Reproducibility inputs

- Exact upstream repositories/commits: [configs/upstream.json](../configs/upstream.json).
- Exact resolved component versions and hashes: [configs/dependencies.lock](../configs/dependencies.lock).
- Arc-only settings: [configs/sdkconfig.arc-live](../configs/sdkconfig.arc-live).
- Toolchain: ESP-IDF v6.0.3; ESP32-S3 target only. Recorded Xtensa tool release: `esp-15.2.0_20251204`; GDB `17.1_20260402`.
- Mac tools installed: CMake, Ninja, dfu-util, Python 3.13, mbedtls and pkgconf. Initial `brew install python3` also installed Python 3.15; the build deliberately used Python 3.13 for dependency compatibility. Historical version strings belong to that installation and are not a guarantee of current Homebrew resolutions.
- The original token file was owner-specified. It was read privately, injected into ignored per-build config and embedded in local firmware. No Wi-Fi SSID/password was compiled in.
- Upstream firmware source remained unmodified. The only custom compiler wrapper applies to **host tests**.

## Build progression

| Build | Configuration/result |
|---|---|
| Default 1.75C Muse | Text-note replies; app `0x211000` bytes; 48% free |
| First live-voice build | Live option on; compiled/image validation passed; hardware exposed internal-memory shortage |
| Final live-voice build | Live + static buffers in PSRAM; app `0x221000` = 2,232,320 bytes; 47% free |

The final table/addresses matched the installed Muse geometry, so pairing NVS could be retained. See the [live artifact manifest](../evidence/arc-muse-1.75c-live-manifest.json) for exact historical binary hashes. A newly rebuilt signed image can differ due to build time/path metadata.

## Checks actually performed

1. Backup hashes, whole-flash compare and factory official asset digest check.
2. Chip identity, memory size and eFuse security-state reads.
3. All exact 1.75C overlay entries matched generated Kconfig for the initial build.
4. Only the 1.75C board selection was enabled; flash size 32 MB, octal PSRAM selected.
5. Secure Boot, flash encryption and pairing eFuse authentication stayed disabled. The SDK development key signs the app without enabling Secure Boot.
6. Compilation, app-slot size check, ESP image checksum/validation hash and packaged-file checksums passed.
7. First host run and focused Mac compatibility reruns are described in [troubleshooting](03-troubleshooting.md). The recorded first run had skips/failures; do not present it as an unqualified clean full-suite pass.
8. The prepared live build passed the 80 voice-call and 42 PTT tests. The later memory change was a configuration/linker-placement change; firmware was rebuilt and hardware-validated, without another complete host-suite run.
9. Each flash was followed by esptool data verification and startup observation. First boot reached display/touch/codec initialization without a panic/reboot loop during observation.
10. User confirmed Wi-Fi/account setup, microphone input, text replies, and finally audible live voice.
11. Final controlled call: HTTP 200; live after approximately 1.94 s; two responses completed; 583 audio frames played; 0 dropped; 0 bad audio; explicit end-call confirmed. User heard Muse.

## Host tests on a fresh Mac

After at least one SDK build populates managed components:

```sh
export IDF_TOOLS_PATH="$PWD/.local/espressif-tools"
. .local/esp-idf/export.sh
export CC="$PWD/scripts/mac-host-cc.py"
export CMAKE_GENERATOR=Ninja
export FREEINK_SOURCE_DIR="$PWD/.local/freeink-sdk"
cd .local/muse/esp32
python -m unittest discover -s tests -p 'test_*.py' -v
```

The bootstrap can fetch the pinned FreeInk test source with `--with-test-sources`. It is for the SDK's cross-board host tests, not the 1.75C display. mbedtls/pkgconf can still need host configuration; inspect skips rather than hiding them. The adapter preserves sanitizers and errors except for platform flag translation and upstream deprecation warnings. Do not use it for firmware cross-compilation.

Focused feature checks:

```sh
python -m unittest discover -s tests -p test_muse_voice_call.py -v
python -m unittest discover -s tests -p test_muse_ptt_ui.py -v
```

No battery runtime, offline response, wake-word, smart-home action, video stream, destructive recovery restoration, OpenAI service or custom-memory integration was acceptance-tested.

## Repository helper verification

The new `scripts/build.py` was executed using the existing pinned Muse/IDF checkouts and installed toolchain. It completed compilation, configuration/security checks, slot-size checks and image checksum/hash validation. The new source repository's seven safety tests and local documentation link checks passed. This rebuild was not flashed. The fresh-machine cloning/installation path in `bootstrap.py` was reviewed and its plan mode checked; it was not reinstalled end-to-end on a clean Mac. Separate evidence: [repository-validation.json](../evidence/repository-validation.json).
