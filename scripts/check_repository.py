#!/usr/bin/env python3
"""Check source publication boundaries. Does not inspect ignored private material."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.bin', '.elf', '.map', '.pem', '.key', '.heic', '.log', '.wav', '.mp3', '.zip'}
SKIP = {'.git', '.local', '__pycache__', '.venv'}
PATTERNS = [
    ('Muse SDK token', re.compile(r'mgst_[A-Za-z0-9_-]{43}(?![A-Za-z0-9_-])')),
    ('OpenAI API key', re.compile(r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}')),
    ('GitHub credential', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})')),
    ('private key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('embedded Wi-Fi setting', re.compile(r'^CONFIG_HOMEHUB_WIFI_(?:SSID|PASSWORD)="[^"\n]+"', re.M)),
    ('embedded SDK token setting', re.compile(r'^CONFIG_GADGET_SDK_TOKEN="(?!\s*"|<|\$)[^"\n]+"', re.M)),
]


def candidates(root):
    root = Path(root)
    if (root / '.git').exists():
        result = subprocess.run(['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                capture_output=True, check=True)
        return sorted({root / name.decode() for name in result.stdout.split(b'\0') if name})
    return sorted(p for p in root.rglob('*') if p.is_file() and not (set(p.relative_to(root).parts) & SKIP))


def scan_file(path):
    path = Path(path)
    issues = []
    if path.suffix.lower() in FORBIDDEN or path.name in {'tokenfile', 'sdkconfig', 'sdkconfig.old', '.env'}:
        issues.append('private/generated artifact')
    if not path.is_file():
        return issues
    if path.is_symlink():
        return issues + ['symlink not allowed in shareable source']
    data = path.read_bytes()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return issues + ['binary file requires explicit review']
    for label, pattern in PATTERNS:
        if pattern.search(text):
            issues.append(label)
    return issues


def main():
    problems = []
    for p in candidates(ROOT):
        rel = p.relative_to(ROOT)
        if set(rel.parts) & SKIP:
            problems.append((rel, ['private directory was tracked']))
            continue
        issues = scan_file(p)
        if issues:
            problems.append((rel, issues))
    for rel, issues in problems:
        # Print labels and paths only, never matching secret values.
        print(f'{rel}: {", ".join(issues)}', file=sys.stderr)
    if problems:
        return 1
    print('Repository boundary check passed; no known credential patterns or private artifacts found.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
