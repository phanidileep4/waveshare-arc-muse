#!/usr/bin/env python3
"""Muse-to-Muse upgrade only. Default is a plan; no erase command is implemented."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from common import LOCAL, FILES, digest, logged_run, private_dir, validate_bundle


def confirmations_ok(args):
    return (args.confirm_flash and args.already_paired_muse
            and args.confirm_board == 'waveshare-1.75c'
            and bool(re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', args.expected_mac or '')))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port', required=True)
    ap.add_argument('--build-dir', type=Path, default=LOCAL / 'build-live')
    ap.add_argument('--confirm-flash', action='store_true', help='Actually write after checks and settings backup')
    ap.add_argument('--already-paired-muse', action='store_true', help='Confirm this is a Muse upgrade, not first migration')
    ap.add_argument('--confirm-board', choices=['waveshare-1.75c'])
    ap.add_argument('--expected-mac', help='MAC verified on the intended physical board; never infer model from MAC alone')
    args = ap.parse_args(argv)
    if not args.confirm_flash:
        print('PLAN ONLY: validate 1.75C images, verify chip/MAC/32 MB flash, back up paired NVS+OTA, write split images.')
        print('No serial port was opened. Actual write needs --confirm-flash --already-paired-muse '
              '--confirm-board waveshare-1.75c --expected-mac <verified-MAC>.')
        return
    if not confirmations_ok(args):
        raise ValueError('All upgrade/model/expected-MAC confirmations are required before device access')
    build = args.build_dir.resolve()
    validate_bundle(build)
    py = LOCAL / 'espressif-tools/python_env/idf6.0_py3.13_env/bin/python'
    if not py.is_file():
        raise ValueError('Pinned IDF Python is missing')
    base = [str(py), '-m', 'esptool', '--chip', 'esp32s3', '--port', args.port]
    identity = subprocess.run(base + ['flash-id'], capture_output=True, text=True, timeout=30)
    text = identity.stdout.lower()
    if identity.returncode or args.expected_mac.lower() not in text or 'detected flash size: 32mb' not in text:
        raise ValueError('Chip/MAC/flash identity check failed; nothing was written')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = LOCAL / 'recovery' / stamp
    if dest.exists():
        raise ValueError('Backup directory already exists; refusing to overwrite it')
    private_dir(dest)
    log = dest / 'upgrade.log'
    backup = dest / 'paired-muse-nvs-and-ota.bin'
    logged_run(base + ['--baud', '460800', 'read-flash', '0x11000', '0xe000', str(backup)], log)
    if backup.stat().st_size != 0xe000:
        raise ValueError('Settings backup size mismatch; refusing firmware write')
    backup.chmod(0o600)
    (dest / 'manifest.json').write_text(json.dumps({'offset': '0x11000', 'bytes': 0xe000,
                                                   'sha256': digest(backup)}, indent=2) + '\n')
    # Avoid executing untrusted @flash_args: fixed addresses and checked file paths.
    command = base + ['--baud', '460800', 'write-flash', '--flash-mode', 'dio',
                      '--flash-freq', '80m', '--flash-size', 'keep']
    for name, address in FILES.items():
        command.extend([address, str(build / name)])
    logged_run(command, log)
    print('Upgrade write/verification finished; NVS was not erased. Verify boot, Wi-Fi, pairing and audible live speech.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
