#!/usr/bin/env python3
"""Fetch pinned public sources and install tools locally. Never flashes."""
import argparse
import os
import shutil
import sys
from common import LOCAL, PINS, check_pin, logged_run, private_dir


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--with-test-sources', action='store_true')
    ap.add_argument('--plan', action='store_true')
    args = ap.parse_args()
    if args.plan:
        print('Clone pinned Muse/ESP-IDF into .local; install ESP32-S3 tools. No device access.')
        return
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError('Use Python 3.13 for the recorded build environment')
    for tool in ('git', 'cmake', 'ninja', 'dfu-util'):
        if not shutil.which(tool):
            raise RuntimeError(f'Missing prerequisite: {tool}; see the step-by-step guide')
    private_dir(LOCAL)
    log = LOCAL / 'logs/bootstrap.log'
    selected = [('muse', 'muse'), ('esp_idf', 'esp-idf')]
    if args.with_test_sources:
        selected.append(('freeink_host_tests', 'freeink-sdk'))
    for name, directory in selected:
        dest = LOCAL / directory
        if not dest.exists():
            logged_run(['git', 'clone', '--no-checkout', PINS[name]['url'], str(dest)], log)
            logged_run(['git', '-C', str(dest), 'checkout', '--detach', PINS[name]['commit']], log)
        check_pin(dest, name)
        if name == 'esp_idf':
            logged_run(['git', '-C', str(dest), 'submodule', 'update', '--init', '--recursive'], log)
    env = {**os.environ, 'IDF_TOOLS_PATH': str(LOCAL / 'espressif-tools')}
    # Ensure install.sh selects the same Python interpreter as this script.
    env['PATH'] = str(__import__('pathlib').Path(sys.executable).parent) + os.pathsep + env['PATH']
    logged_run(['bash', str(LOCAL / 'esp-idf/install.sh'), 'esp32s3'], log, env=env)
    print('Pinned sources and ESP32-S3 toolchain ready. Build separately; nothing was flashed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
