#!/usr/bin/env python3
"""Build the exact Arc live profile with a private file-supplied SDK token."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
from common import ROOT, LOCAL, PINS, FILES, check_pin, digest, logged_run, private_dir


def put_token(config, token_path):
    tokens = set(re.findall(r'mgst_[A-Za-z0-9_-]{43}(?![A-Za-z0-9_-])', Path(token_path).read_text()))
    if len(tokens) != 1:
        raise ValueError('Token file must contain exactly one distinct Muse SDK token')
    value = tokens.pop()
    if value[-1] not in 'AEIMQUYcgkosw048':
        raise ValueError('SDK token encoding is not canonical')
    text = config.read_text() if config.exists() else ''
    text = re.sub(r'^CONFIG_GADGET_SDK_TOKEN=.*\n?', '', text, flags=re.M)
    config.write_text(text + '\nCONFIG_GADGET_SDK_TOKEN="' + value + '"\n')
    config.chmod(0o600)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', action='store_true')
    args = ap.parse_args()
    if args.plan:
        print('Build pinned esp32s3 / waveshare_s3_175c with live voice + static buffers in PSRAM. No flash.')
        return
    token_path = os.environ.get('ARC_SDK_TOKEN_FILE')
    if not token_path:
        raise RuntimeError('Set ARC_SDK_TOKEN_FILE to a private file path; never pass the token itself')
    check_pin(LOCAL / 'muse', 'muse')
    check_pin(LOCAL / 'esp-idf', 'esp_idf')
    src = LOCAL / 'muse/esp32'
    shutil.copyfile(ROOT / 'configs/dependencies.lock', src / 'dependencies.lock')
    build = private_dir(LOCAL / 'build-live')
    put_token(build / 'sdkconfig', token_path)
    defaults = ';'.join([
        'sdkconfig.defaults', 'devices/sdkconfig.muse',
        'devices/sdkconfig.muse-waveshare-s3-175c', str(ROOT / 'configs/sdkconfig.arc-live')])
    env = {**os.environ, 'IDF_TOOLS_PATH': str(LOCAL / 'espressif-tools'),
           'ARC_IDF_EXPORT': str(LOCAL / 'esp-idf/export.sh')}
    command = ['idf.py', '-B', str(build), '-DIDF_TARGET=esp32s3',
               '-DSDKCONFIG=' + str(build / 'sdkconfig'), '-DSDKCONFIG_DEFAULTS=' + defaults, 'build']
    # Pass all dynamic arguments as argv, never interpolated into shell code.
    shell = ['bash', '-c', 'set -e; . "$ARC_IDF_EXPORT"; exec "$@"', 'arc-build']
    logged_run(shell + command, LOCAL / 'logs/build.log', cwd=src, env=env)
    config = (build / 'sdkconfig').read_text()
    expected = ['CONFIG_MUSE_BOARD_WAVESHARE_S3_175C=y', 'CONFIG_IDF_TARGET="esp32s3"',
                'CONFIG_ESPTOOLPY_FLASHSIZE="32MB"', 'CONFIG_SPIRAM_MODE_OCT=y',
                'CONFIG_MUSE_REALTIME_VOICE=y', 'CONFIG_MUSE_STATIC_BUFFERS_IN_PSRAM=y']
    for item in expected:
        if item not in config.splitlines():
            raise RuntimeError('Required build setting missing: ' + item.split('=')[0])
    for key in ['CONFIG_SECURE_BOOT', 'CONFIG_FLASH_ENCRYPTION_ENABLED', 'CONFIG_HOMEHUB_PAIRING_EFUSE_AUTH']:
        if key + '=y' in config.splitlines():
            raise RuntimeError('Unsafe change to recoverability: ' + key)
    app_bytes = (build / 'muse-gadget.bin').stat().st_size
    if not 0 < app_bytes <= 0x400000:
        raise RuntimeError('Application exceeds the 4 MiB slot')
    py = next((LOCAL / 'espressif-tools/python_env').glob('idf6.0_py3.13_env/bin/python'))
    image_log = LOCAL / 'logs/image-info.log'
    if image_log.exists():
        image_log.unlink()
    logged_run([str(py), '-m', 'esptool', '--chip', 'esp32s3', 'image-info', str(build / 'muse-gadget.bin')],
               image_log)
    image_info = image_log.read_text()
    if not (re.search(r'Checksum:.*\(valid\)', image_info)
            and re.search(r'Validation hash:.*\(valid\)', image_info)):
        raise RuntimeError('ESP image checksum/hash validation failed; inspect the private image log')
    manifest = {'board': 'Waveshare ESP32-S3-Touch-AMOLED-1.75C', 'sdk_commit': PINS['muse']['commit'],
                'esp_idf_commit': PINS['esp_idf']['commit'], 'app_bytes': app_bytes,
                'sdk_token_embedded': True, 'files': [
                    {'path': n, 'bytes': (build / n).stat().st_size, 'sha256': digest(build / n)} for n in FILES]}
    (build / 'arc-build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Arc build verified. Private artifacts: .local/build-live. Nothing was flashed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, StopIteration) as exc:
        print(str(exc) or 'Missing toolchain environment; run bootstrap.py first', file=sys.stderr)
        raise SystemExit(1)
