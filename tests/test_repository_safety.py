"""Test accidental hardware writes and secret/artifact publication boundaries."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build
import common
import flash
import check_repository as check


class SafeDefaults(unittest.TestCase):
    def test_dry_run_never_opens_device_or_checks_toolchain(self):
        with patch.object(flash.subprocess, 'run', side_effect=AssertionError('device accessed')):
            flash.main(['--port', '/dev/nonexistent'])

    def test_incomplete_approval_refuses_before_device_access(self):
        with patch.object(flash.subprocess, 'run', side_effect=AssertionError('device accessed')):
            with self.assertRaisesRegex(ValueError, 'confirmations'):
                flash.main(['--port', '/dev/nonexistent', '--confirm-flash'])

    def test_mutated_firmware_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            files = []
            for name in common.FILES:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'original')
                files.append({'path': name, 'bytes': 8, 'sha256': common.digest(p)})
            manifest = {'board': 'Waveshare ESP32-S3-Touch-AMOLED-1.75C',
                        'sdk_commit': common.PINS['muse']['commit'], 'app_bytes': 8, 'files': files}
            (root / 'arc-build-manifest.json').write_text(json.dumps(manifest))
            common.validate_bundle(root)
            (root / 'muse-gadget.bin').write_bytes(b'modified')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                common.validate_bundle(root)

    def test_path_escape_and_duplicate_entries_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = {'board': 'Waveshare ESP32-S3-Touch-AMOLED-1.75C',
                 'sdk_commit': common.PINS['muse']['commit'], 'app_bytes': 8,
                 'files': [{'path': '../private.bin'}] * 4}
            (root / 'arc-build-manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'file set'):
                common.validate_bundle(root)


class Privacy(unittest.TestCase):
    def test_real_shaped_token_rejected_without_printing_value(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'notes.md'
            p.write_text('mgst_' + 'A' * 43)
            self.assertIn('Muse SDK token', check.scan_file(p))

    def test_dump_and_wifi_setting_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'backup.bin'
            p.write_bytes(b'sensitive')
            self.assertIn('private/generated artifact', check.scan_file(p))
            p = Path(d) / 'settings.txt'
            p.write_text('CONFIG_HOMEHUB_WIFI_PASSWORD="' + 'test-private-value' + '"')
            self.assertIn('embedded Wi-Fi setting', check.scan_file(p))

    def test_private_token_injection_preserves_other_settings(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            key = root / 'key'
            key.write_text('mgst_' + 'A' * 43)
            config = root / 'sdkconfig'
            config.write_text('CONFIG_MUSE_REALTIME_VOICE=y\n')
            build.put_token(config, key)
            self.assertIn('CONFIG_MUSE_REALTIME_VOICE=y', config.read_text())
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
