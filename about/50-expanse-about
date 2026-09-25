#!/usr/bin/env python3
"""Select Expanse About branding; retain the user's branding for other themes."""
import fcntl
import os
from pathlib import Path
import sys

home = Path.home()
state = home / '.local/state/omarchy-expanse/about'
target = home / '.config/omarchy/branding/about.txt'
runtime = home / '.local/share/omarchy-expanse/about'
theme_file = home / '.local/state/omarchy/current/theme.name'
state.mkdir(parents=True, exist_ok=True)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.expanse-new')
    temporary.write_bytes(content)
    temporary.replace(path)


def switch_file(target, artwork, directory, active, baseline=None):
    directory.mkdir(parents=True, exist_ok=True)
    previous = directory / 'previous.txt'
    applied = directory / 'applied.txt'
    absent = directory / 'previous-absent'
    link = directory / 'previous-link'
    current = target.read_bytes() if target.exists() else None
    if active:
        if not applied.exists():
            if target.is_symlink():
                link.write_text(os.readlink(target))
            elif current is None:
                absent.touch()
            else:
                write(previous, baseline if baseline is not None else current)
                previous.chmod(target.stat().st_mode & 0o777)
        elif target.is_symlink() or current != applied.read_bytes():
            # Preserve a manual branding edit until the next theme activation.
            return
        write(target, artwork)
        write(applied, artwork)
    elif applied.exists():
        # A manual edit made after activation belongs to the user; keep it.
        if not target.is_symlink() and current == applied.read_bytes():
            if link.exists():
                temporary = target.with_name(target.name + '.expanse-new')
                temporary.symlink_to(link.read_text())
                temporary.replace(target)
            elif previous.exists():
                write(target, previous.read_bytes())
                target.chmod(previous.stat().st_mode & 0o777)
            elif absent.exists():
                target.unlink(missing_ok=True)
        for path in (previous, applied, absent, link):
            path.unlink(missing_ok=True)


with (state / 'lock').open('w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    # Read the current theme rather than a potentially stale queued hook argument.
    theme = theme_file.read_text().strip() if theme_file.exists() else ''
    active = theme == 'expanse' and '--restore' not in sys.argv
    # Load every required asset before changing either managed file.
    artwork = (runtime / 'logo.txt').read_bytes() if active else None
    config = (runtime / 'fastfetch.jsonc').read_bytes() if active else None
    baseline = None
    if active and target.exists() and not (state / 'applied.txt').exists():
        original = (runtime / 'rocinante.txt').read_bytes()
        stock = Path(os.environ.get('OMARCHY_PATH', '/usr/share/omarchy')) / 'icon.txt'
        if target.read_bytes() in (original, artwork) and stock.exists():
            baseline = stock.read_bytes()
    # Keep the original logo state location for upgrades from the logo-only hook.
    switch_file(target, artwork, state, active, baseline)
    switch_file(home / '.config/fastfetch/config.jsonc', config, state / 'fastfetch', active)
