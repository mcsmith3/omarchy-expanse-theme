#!/usr/bin/env python3
"""Install Expanse's screensaver with a single launch-command change to Omarchy idle."""
import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = 'omarchy-launch-screensaver")'
CUSTOM = '\\"$HOME/.local/share/omarchy-expanse/launch-screensaver\\"")'


def patch_service(text):
    if text.count(ORIGINAL) != 1:
        raise ValueError("Unsupported Omarchy idle service; no files changed.")
    return text.replace(ORIGINAL, CUSTOM, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check compatibility without making changes")
    args = parser.parse_args()
    home = Path.home()
    omarchy = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
    stock = (omarchy / "shell/plugins/services/idle/Service.qml").read_text()
    updated = patch_service(stock)
    plugin_id = getpass.getuser() + ".idle"
    target = home / ".config/omarchy/plugins" / plugin_id
    if target.exists():
        manifest = json.loads((target / "manifest.json").read_text())
        if manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.idle":
            raise ValueError(f"{target} is not a clone of omarchy.idle.")
        if (target / "Service.qml").read_text() not in (stock, updated):
            raise ValueError("Your local idle plugin has other changes; merge manually. No files changed.")
    for command in ("qs", "omarchy", "omarchy-shell", "flock", "pgrep"):
        if not shutil.which(command):
            raise ValueError(f"Required command is missing: {command}")
    version = subprocess.check_output(["qs", "--version"], text=True)
    match = re.search(r"Quickshell (\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (0, 3):
        raise ValueError("Quickshell 0.3 or later is required for the screensaver app ID.")
    for asset in ("shell.qml", "pixel-dissolve.frag.qsb", "launch-screensaver", "images/rocinante.png", "images/tycho.png", "images/nauvoo.png", "images/ring.png", "images/ceres.jpg", "images/eros.jpg", "images/ganymede.jpg", "images/io.jpg"):
        if not (ROOT / "screensaver" / asset).is_file():
            raise ValueError(f"Missing screensaver asset: {asset}")
    if args.check:
        print("Compatible idle service and complete screensaver assets. No files changed.")
        return
    status = json.loads(subprocess.check_output(["omarchy-shell", "lock", "status"], text=True))
    if status.get("locked") or status.get("requested") or status.get("secure"):
        raise ValueError("Unlock your session before installing.")
    if not target.exists():
        subprocess.run(["omarchy", "plugin", "clone", "omarchy.idle"], check=True)
    backup = home / ".local/state/omarchy/backups" / ("expanse-screensaver-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    shutil.copytree(target, backup / "idle-plugin")
    runtime = home / ".local/share/omarchy-expanse"
    if runtime.exists():
        shutil.copytree(runtime, backup / "screensaver")
    runtime.mkdir(parents=True, exist_ok=True)
    # Stop a previous instance before replacing its images or shader.
    subprocess.run(["qs", "ipc", "-p", str(runtime / "org.omarchy.screensaver"), "call", "screensaver", "quit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copytree(ROOT / "screensaver", runtime / "org.omarchy.screensaver", dirs_exist_ok=True)
    shutil.copy2(ROOT / "screensaver/launch-screensaver", runtime / "launch-screensaver")
    (runtime / "launch-screensaver").chmod(0o755)
    temporary = target / "Service.qml.new"
    temporary.write_text(updated)
    temporary.replace(target / "Service.qml")
    subprocess.run(["omarchy-shell", "shell", "rescanPlugins"], check=True)
    subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
    print(f"Installed Expanse screensaver. Backup: {backup}")
    print("Activate while unlocked: omarchy restart shell")
    print(f"Preview: {runtime}/launch-screensaver --preview")
    print(f"Restore stock idle service: omarchy plugin disable {plugin_id}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
