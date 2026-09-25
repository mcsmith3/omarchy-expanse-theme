"""Exercise theme switching against isolated user homes."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AboutSwitching(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.logo = self.home / '.config/omarchy/branding/about.txt'
        self.config = self.home / '.config/fastfetch/config.jsonc'
        self.theme = self.home / '.local/state/omarchy/current/theme.name'
        self.runtime = self.home / '.local/share/omarchy-expanse/about'
        self.state = self.home / '.local/state/omarchy-expanse/about'
        for path in (self.logo, self.config, self.theme):
            path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / 'about', self.runtime)
        self.stock = self.home / 'stock'
        self.stock.mkdir()
        (self.stock / 'icon.txt').write_bytes(b'STOCK LOGO')
        self.env = dict(os.environ, HOME=str(self.home), OMARCHY_PATH=str(self.stock))

    def switch(self, theme, *args):
        self.theme.write_text(theme)
        subprocess.run([sys.executable, str(ROOT / 'about/50-expanse-about'), *args],
                       env=self.env, check=True, capture_output=True)

    def test_switch_restores_both_and_repeated_activation_keeps_originals(self):
        self.logo.write_bytes(b'MY LOGO')
        self.config.write_bytes(b'{"modules":["cpu"]}')
        self.config.chmod(0o600)
        self.switch('expanse')
        self.assertEqual(self.config.read_bytes(), (self.runtime / 'fastfetch.jsonc').read_bytes())
        self.assertIn(b'REMEMBER THE CANT', self.logo.read_bytes())
        self.switch('expanse')
        self.switch('other')
        self.assertEqual(self.logo.read_bytes(), b'MY LOGO')
        self.assertEqual(self.config.read_bytes(), b'{"modules":["cpu"]}')
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)

    def test_absent_config_returns_to_system_default(self):
        self.switch('other')
        self.assertFalse(self.config.exists())
        self.switch('expanse')
        self.switch('other')
        self.assertFalse(self.config.exists())
        self.assertFalse(self.logo.exists())

    def test_manual_edits_are_independent(self):
        self.switch('expanse')
        self.logo.write_bytes(b'MANUAL LOGO')
        (self.runtime / 'fastfetch.jsonc').write_bytes(b'UPDATED CONFIG')
        self.switch('expanse')
        self.assertEqual(self.config.read_bytes(), b'UPDATED CONFIG')
        self.config.write_bytes(b'MANUAL CONFIG')
        self.switch('other')
        self.assertEqual(self.logo.read_bytes(), b'MANUAL LOGO')
        self.assertEqual(self.config.read_bytes(), b'MANUAL CONFIG')
        self.switch('expanse')
        self.switch('other')
        self.assertEqual(self.config.read_bytes(), b'MANUAL CONFIG')

    def test_symlink_and_dangling_symlink_are_restored(self):
        for present in (True, False):
            with self.subTest(present=present):
                original = self.config.parent / 'personal.jsonc'
                if present:
                    original.write_bytes(b'PERSONAL CONFIG')
                else:
                    original.unlink()
                self.config.symlink_to('personal.jsonc')
                self.switch('expanse')
                self.assertFalse(self.config.is_symlink())
                self.switch('other')
                self.assertTrue(self.config.is_symlink())
                self.assertEqual(os.readlink(self.config), 'personal.jsonc')
                if present:
                    self.assertEqual(original.read_bytes(), b'PERSONAL CONFIG')
                self.config.unlink()

    def test_upgrade_from_logo_only_retains_original_backup(self):
        old = (ROOT / 'about/rocinante.txt').read_bytes()
        self.logo.write_bytes(old)
        self.state.mkdir(parents=True)
        (self.state / 'applied.txt').write_bytes(old)
        (self.state / 'previous.txt').write_bytes(b'ORIGINAL LOGO')
        self.switch('expanse')
        self.assertIn(b'REMEMBER THE CANT', self.logo.read_bytes())
        self.switch('other')
        self.assertEqual(self.logo.read_bytes(), b'ORIGINAL LOGO')
        self.assertFalse(self.config.exists())

    def test_existing_rocinante_restores_stock(self):
        self.logo.write_bytes((ROOT / 'about/rocinante.txt').read_bytes())
        self.switch('expanse')
        self.switch('other')
        self.assertEqual(self.logo.read_bytes(), b'STOCK LOGO')

    def test_uninstall_restores_even_when_expanse_is_active(self):
        self.config.write_bytes(b'ORIGINAL CONFIG')
        self.switch('expanse')
        self.switch('expanse', '--restore')
        self.assertEqual(self.config.read_bytes(), b'ORIGINAL CONFIG')
        self.assertFalse(self.logo.exists())

    def test_missing_asset_leaves_existing_files_untouched(self):
        self.config.write_bytes(b'ORIGINAL CONFIG')
        self.logo.write_bytes(b'ORIGINAL LOGO')
        (self.runtime / 'fastfetch.jsonc').unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            self.switch('expanse')
        self.assertEqual(self.config.read_bytes(), b'ORIGINAL CONFIG')
        self.assertEqual(self.logo.read_bytes(), b'ORIGINAL LOGO')


if __name__ == '__main__':
    unittest.main()
