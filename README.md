# Arc companion

Arc is a Waveshare **ESP32-S3-Touch-AMOLED-1.75C** running the official Muse Gadget SDK. This repository records the November 5–6, 2026 migration from working Xiaozhi firmware to verified Muse live voice.

**Current result:** Wi-Fi connected, Muse paired, spoken replies heard by the owner. A live-call test returned HTTP 200, played 583 audio frames with zero dropped/bad audio frames, and ended with server confirmation. OpenAI integration is deferred; it has not been implemented.

## Start here

| Need | Document |
|---|---|
| Start from a new Mac and board | [Step-by-step guide](docs/01-step-by-step.md) |
| Use Arc today | [Daily use and capabilities](docs/02-daily-use.md) |
| Diagnose a problem | [Troubleshooting and findings](docs/03-troubleshooting.md) |
| Understand what happened | [Session chronology](docs/04-session-history.md) |
| Restore firmware or protect pairing | [Backup and recovery](docs/05-backup-and-recovery.md) |
| Identify the exact hardware | [Hardware and battery](docs/06-hardware-and-battery.md) |
| Reproduce the working build | [Build and validation](docs/07-build-and-validation.md) |
| Resume OpenAI work later | [OpenAI roadmap](docs/08-openai-roadmap.md) |
| Find original sources and context limits | [Sources and provenance](docs/09-sources-and-provenance.md) |
| Understand private/local material | [Secrets and archive policy](docs/10-secrets-and-archive.md) |

## The working configuration

```ini
CONFIG_MUSE_REALTIME_VOICE=y
CONFIG_MUSE_STATIC_BUFFERS_IN_PSRAM=y
```

Both settings matter. Live voice without the external-memory setting left no sufficiently large internal heap block for Muse's 8 KiB connection task. Moving the SDK's avatar/audio static buffers into PSRAM fixed the observed connection failure.

| Item | Verified selection |
|---|---|
| Board | Waveshare ESP32-S3-Touch-AMOLED-1.75C, Rev 1.1 visible in owner's photo |
| Target | `esp32s3` |
| Flash / PSRAM | 32 MiB / 8 MiB octal |
| Screen | 466 × 466 round AMOLED |
| Muse commit | `463bd2a05380fea4211b0099ad0f70933c108b20` |
| ESP-IDF | `v6.0.3`, commit `76f5dedd9950a3012fee8fb7d5586df21fc67802` |
| Board defaults | `sdkconfig.defaults;devices/sdkconfig.muse;devices/sdkconfig.muse-waveshare-s3-175c` |
| Arc additions | [configs/sdkconfig.arc-live](configs/sdkconfig.arc-live) |
| Installed app | 2,232,320 bytes; 47% of the 4 MiB slot free |
| Secure Boot / flash encryption | Disabled; no eFuses were programmed |

## Repository versus private archive

Git contains documentation, source pins, the dependency lock, safe configuration overlays, scripts, checksums, and sanitized evidence. It deliberately excludes SDK/API tokens, Wi-Fi credentials, generated configurations, raw logs, token-bearing firmware binaries, and flash/NVS dumps. Those are retained locally in ignored `.local/` and the original workspace. See the [archive policy](docs/10-secrets-and-archive.md).

No script flashes automatically. [scripts/flash.py](scripts/flash.py) defaults to a plan and requires explicit confirmation flags for a real write. No hardware operations are necessary to read or validate this repository.

## Local checks

```sh
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

The assistant's original failed attempts and later corrections are recorded as findings, not presented as steps that all succeeded.
