# Backup, upgrade and recovery

## What each backup means

| Material | Purpose | Git policy |
|---|---|---|
| Original 16 MiB Xiaozhi dump | Historical partial backup; first half of full flash | Private local only |
| Verified 32 MiB Xiaozhi dump | Return to the saved working Xiaozhi firmware/settings | Private local only |
| Official factory-only image | Restore the vendor factory demo, not personal Xiaozhi configuration | Local; official download URL/checksum tracked |
| Paired Muse NVS + OTA snapshot | Preserve Muse Wi-Fi/account state immediately before live update | Private local only |
| Working Muse split binaries | Roll back to a known build, but contain the SDK token | Private local only |
| JSON manifests and hashes | Verify identity, size and provenance | Tracked |

The local archive inventory records where the personal copies are kept. Copying this Git repository to another computer does **not** copy private recovery files. Back them up separately to an encrypted location controlled by the owner.

## Verified historical hashes

| File | Bytes | SHA-256 |
|---|---:|---|
| `arc-xiaozhi-original.bin` | 16,777,216 | `b573297f2ea897f76f16d907c00d26c47dbe75701d6f7dc03808872872d5823f` |
| `arc-xiaozhi-full-32mb.bin` | 33,554,432 | `f1a05e9e2bab5048e9bbbb7f81349583c0359337bc295f2582e639205a5879c3` |
| `ESP32-S3-Touch-AMOLED-1.75C-FactoryOnly-260114.bin` | 33,488,896 | `46e65fb708f325f6830d6f14ecbba3d357dbdab6a939e13fdf2206e147c063d2` |

The whole 32 MiB dump matched the device before the migration. The factory image matched official release asset metadata. Both images' ESP32-S3 bootloader checksums and validation hashes were valid.

## Partition layouts are different

Xiaozhi table: `0x8000`.

| Xiaozhi partition | Offset | Size |
|---|---|---|
| nvsfactory | `0x9000` | `0x32000` |
| nvs | `0x3b000` | `0xd2000` |
| otadata | `0x10d000` | `0x2000` |
| phy_init | `0x10f000` | `0x1000` |
| factory | `0x110000` | `0x900000` |
| ota_0 | `0xa10000` | `0x3f0000` |
| ota_1 | `0xe00000` | `0x3f0000` |
| assets | `0x11f0000` | `0x900000` |
| storage | `0x1af0000` | `0x500000` |

Muse table: `0x10000`; source is upstream `partitions_muse.csv`.

| Muse partition | Offset | Size |
|---|---|---|
| nvs | `0x11000` | `0xc000` |
| otadata | `0x1d000` | `0x2000` |
| phy_init | `0x1f000` | `0x1000` |
| ota_0 | `0x20000` | 4 MiB |
| ota_1 | `0x420000` | 4 MiB |
| prod_data | `0x820000` | `0x1000` |
| prod_bak | `0x821000` | `0x1000` |

Muse's geometry does not consume every byte of 32 MiB flash. First migration initialized only the new NVS region. Later Muse upgrades wrote the split image set and left NVS untouched. No full-chip erase or eFuse programming was performed.

## Back up paired Muse settings before an update

Use IDF's Python, correct port, a private directory and a new filename:

```sh
umask 077
python -m esptool --chip esp32s3 --port "$ARC_PORT" --baud 460800 \
  read-flash 0x11000 0xe000 paired-muse-nvs-and-ota.bin
shasum -a 256 paired-muse-nvs-and-ota.bin
```

This is **56 KiB**: 48 KiB NVS plus 8 KiB OTA state. It is not a complete firmware backup and must not be described as one. Its contents are personal, even when encrypted transport is used to communicate with Muse. Current NVS is plaintext; enabling NVS encryption was not part of this project because it can provision an eFuse key and changes recovery assumptions.

## Restore the saved Xiaozhi state

Only after deciding to replace the current firmware and confirming board, port and backup hash:

```sh
# DESTRUCTIVE: restores saved firmware and old settings across the chip.
python -m esptool --chip esp32s3 --port "$ARC_PORT" --baud 460800 \
  write-flash --flash-size keep 0x0 arc-xiaozhi-full-32mb.bin
python -m esptool --chip esp32s3 --port "$ARC_PORT" \
  verify-flash 0x0 arc-xiaozhi-full-32mb.bin
```

Restoring an old dump also restores old credentials/tokens; revoked credentials may no longer work. A successful restoration was **not performed** in this session. Recoverability was supported by verified backup integrity and chip access, not demonstrated by a destructive restore test.

## Restore a Muse build

Use the known split-image package's `flash_args` with the exact matching files. Keep NVS if you want current Wi-Fi/pairing to survive. Do not run the first-migration NVS erase. Before restoring an old NVS snapshot, back up current NVS and consider whether paired tokens have since changed. Do not restore OTA state independently of understanding which app slot it selects.

Never write `muse-gadget.bin` at `0x0`. That address belongs to the bootloader. Never mix image components from different builds or assume a 1.85C build is interchangeable.
