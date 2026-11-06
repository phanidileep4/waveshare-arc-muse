"""Shared pinned paths and artifact checks. Never import credentials."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'
PINS = json.loads((ROOT / 'configs/upstream.json').read_text())
FILES = {
    'bootloader/bootloader.bin': '0x0',
    'partition_table/partition-table.bin': '0x10000',
    'ota_data_initial.bin': '0x1d000',
    'muse-gadget.bin': '0x20000',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def private_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


def check_pin(path, name):
    if not Path(path).is_dir():
        raise ValueError(f'{name} checkout missing; run bootstrap.py first')
    result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f'{name} checkout is not readable as a Git repository')
    actual = result.stdout.strip()
    if actual != PINS[name]['commit']:
        raise ValueError(f'{name} is not at the recorded commit')


def logged_run(args, log, cwd=None, env=None):
    private_dir(Path(log).parent)
    with open(log, 'a', encoding='utf-8') as stream:
        os.chmod(log, 0o600)
        result = subprocess.run(args, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Command failed; inspect the private log: {log}')


def validate_bundle(path):
    """Reject modified files, unexpected geometry and path escapes before writes."""
    path = Path(path).resolve()
    m = json.loads((path / 'arc-build-manifest.json').read_text())
    if m.get('board') != 'Waveshare ESP32-S3-Touch-AMOLED-1.75C':
        raise ValueError('Wrong board manifest')
    if m.get('sdk_commit') != PINS['muse']['commit']:
        raise ValueError('Unexpected Muse source revision')
    entries = m.get('files', [])
    if len(entries) != len(FILES) or {e['path'] for e in entries} != set(FILES):
        raise ValueError('Unexpected firmware file set')
    for entry in entries:
        p = (path / entry['path']).resolve()
        if not p.is_relative_to(path) or not p.is_file():
            raise ValueError('Firmware path escaped the build directory')
        if p.stat().st_size != entry['bytes'] or digest(p) != entry['sha256']:
            raise ValueError(f'Firmware checksum mismatch: {entry["path"]}')
    if m.get('app_bytes', 0) <= 0 or m['app_bytes'] > 0x400000:
        raise ValueError('Application does not fit the 4 MiB slot')
    return m
