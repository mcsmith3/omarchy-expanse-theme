#!/usr/bin/env python3
"""Install theme-aware Rocinante About branding for Omarchy."""
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
home = Path.home()
parser = argparse.ArgumentParser(description=__doc__)
mode = parser.add_mutually_exclusive_group()
mode.add_argument('--check', action='store_true', help='validate without changing files')
mode.add_argument('--uninstall', action='store_true', help='restore branding and remove the hook')
args = parser.parse_args()
hook = home / '.config/omarchy/hooks/theme-set.d/50-expanse-about'
runtime = home / '.local/share/omarchy-expanse/about/rocinante.txt'

if args.uninstall:
    if hook.exists():
        subprocess.run([str(hook), '--restore'], check=True)
        hook.unlink()
    runtime.unlink(missing_ok=True)
    print('Removed Expanse About integration; previous branding restored where unchanged.')
else:
    source = root / 'about/rocinante.txt'
    source_hook = root / 'about/50-expanse-about'
    for path in (source, source_hook):
        if not path.is_file():
            parser.error(f'Missing asset: {path}')
    if not shutil.which('omarchy') or not shutil.which('fastfetch'):
        parser.error('Omarchy and Fastfetch are required.')
    if args.check:
        print('About artwork and hook are ready. No files changed.')
    else:
        backup = home / '.local/state/omarchy/backups' / ('expanse-about-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        backup.mkdir(parents=True)
        for path, name in ((home / '.config/omarchy/branding/about.txt', 'about.txt'),
                           (hook, '50-expanse-about'), (runtime, 'rocinante.txt')):
            if path.exists():
                shutil.copy2(path, backup / name)
        runtime.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, runtime)
        subprocess.run(['omarchy', 'hook', 'install', 'theme-set', str(source_hook)], check=True)
        subprocess.run([str(hook)], check=True)
        print(f'Installed Expanse About branding. Backup: {backup}')
        print('View it with: omarchy launch about')
