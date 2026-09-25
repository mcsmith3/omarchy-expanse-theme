#!/usr/bin/env python3
"""Install Expanse visuals onto a supported clone of Omarchy's current locker."""

import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("This Omarchy lock-screen version is not supported; no files changed.")
    return text.replace(old, new, 1)


def service_source(stock):
    stock = replace_once(
        stock,
        '  readonly property string currentBackgroundLink: stateHome + "/omarchy/current/background"',
        '  readonly property string currentBackgroundLink: stateHome + "/omarchy/current/background"\n'
        '  readonly property string themeLockBackground: stateHome + "/omarchy/current/theme/lock-background.png"\n'
        '  readonly property string rocinanteBackground: stateHome + "/omarchy/current/theme/lock-rocinante.png"',
    )
    return replace_once(
        stock,
        '    command: ["readlink", "-f", root.currentBackgroundLink]',
        '    // Prefer Expanse artwork, then another theme\'s lock image, then its wallpaper.\n'
        '    command: ["bash", "-c", "for path in \\"$@\\"; do if [[ -f $path ]]; then readlink -f -- \\"$path\\"; exit; fi; done", '
        '"omarchy-lock-background", root.rocinanteBackground, root.themeLockBackground, root.currentBackgroundLink]',
    )


def view_source(stock):
    stock = replace_once(stock, '  property int backgroundVersion: 0',
        '  property int backgroundVersion: 0\n'
        '  readonly property bool handTerminalLayout: backgroundPath.endsWith("/lock-rocinante.png")\n'
        '  readonly property bool dedicatedLockBackground: handTerminalLayout || backgroundPath.endsWith("/lock-background.png")')
    for old, new in [
        ('readonly property int fieldWidth: 381', 'readonly property int fieldWidth: handTerminalLayout ? 288 : 381'),
        ('readonly property int fieldHeight: 67', 'readonly property int fieldHeight: handTerminalLayout ? 60 : 67'),
        ('readonly property int outlineThickness: 3', 'readonly property int outlineThickness: handTerminalLayout ? 1 : 3'),
        ('readonly property int fieldFontSize: Math.round(Style.font.heading * 1.125)',
         'readonly property int fieldFontSize: handTerminalLayout ? 16 : Math.round(Style.font.heading * 1.125)'),
        ('readonly property int passwordDotFontSize: Math.round(Style.font.heading * 1.33)',
         'readonly property int passwordDotFontSize: handTerminalLayout ? 20 : Math.round(Style.font.heading * 1.33)'),
        ('    MultiEffect {', '    MultiEffect {\n      visible: !root.dedicatedLockBackground'),
        ('blurEnabled: root.loadBackground && wallpaper.status === Image.Ready',
         'blurEnabled: !root.dedicatedLockBackground && root.loadBackground && wallpaper.status === Image.Ready'),
        ('      color: Color.lock.background', '      color: root.handTerminalLayout ? "#dd071018" : Color.lock.background'),
        ('      radius: Style.cornerRadius', '      radius: root.handTerminalLayout ? 0 : Style.cornerRadius'),
        ('      anchors.centerIn: parent\n      color:',
         '      anchors.centerIn: parent\n      anchors.verticalCenterOffset: root.handTerminalLayout ? 55 : 0\n      color:'),
    ]:
        stock = replace_once(stock, old, new)
    stock = replace_once(stock, '    BorderSurface {\n      id: inputField', '''    Item {
      id: fieldContainer
      width: root.handTerminalLayout ? 350 : parent.width
      height: root.handTerminalLayout ? 680 : parent.height
      anchors.centerIn: parent
      scale: root.handTerminalLayout ? Math.min(1, (root.width - 32) / 350, (root.height - 40) / 680) : 1

      HandTerminal {
        anchors.fill: parent
        visible: root.handTerminalLayout
        authenticating: root.authenticatingPassword
        failed: root.failureMessage.length > 0
        fingerprintAvailable: root.fingerprintConfigured
        fontFamily: Style.font.family
        onActivate: {
          root.wakeRequested()
          root.forcePasswordFocus()
          if (root.inputEnabled && !root.authenticatingPassword) passwordInput.accepted()
        }
      }

    BorderSurface {
      id: inputField''')
    if not stock.endswith('    }\n  }\n}\n'):
        raise ValueError("Unexpected LockView structure; no files changed.")
    return stock[:-len('    }\n  }\n}\n')] + '    }\n    }\n  }\n}\n'


def legacy_sources(service, view):
    """Recognize the first locally installed Expanse background customization."""
    service = service.replace(
        '  readonly property string currentBackgroundLink: stateHome + "/omarchy/current/background"',
        '  readonly property string currentBackgroundLink: stateHome + "/omarchy/current/background"\n'
        '  readonly property string themeLockBackground: stateHome + "/omarchy/current/theme/lock-background.png"')
    service = service.replace('    command: ["readlink", "-f", root.currentBackgroundLink]',
        '    // A theme may supply dedicated lock artwork; otherwise retain the desktop background.\n'
        '    command: ["bash", "-c", "if [[ -f $1 ]]; then readlink -f -- \\"$1\\"; else readlink -f -- \\"$2\\"; fi", "omarchy-lock-background", root.themeLockBackground, root.currentBackgroundLink]')
    view = view.replace('  property int backgroundVersion: 0', '  property int backgroundVersion: 0\n'
        '  readonly property bool dedicatedLockBackground: backgroundPath.endsWith("/lock-background.png")')
    view = view.replace('    MultiEffect {', '    MultiEffect {\n'
        '      // Dedicated artwork is composed for the password field and stays sharp.\n'
        '      visible: !root.dedicatedLockBackground')
    view = view.replace('blurEnabled: root.loadBackground && wallpaper.status === Image.Ready',
        'blurEnabled: !root.dedicatedLockBackground && root.loadBackground && wallpaper.status === Image.Ready')
    return service, view


def shell(*args):
    return subprocess.check_output(["omarchy-shell", *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate compatibility without changing files")
    args = parser.parse_args()
    omarchy = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
    source = omarchy / "shell/plugins/lock"
    stock_service = (source / "Service.qml").read_text()
    stock_view = (source / "LockView.qml").read_text()
    service, view = service_source(stock_service), view_source(stock_view)
    legacy_service, legacy_view = legacy_sources(stock_service, stock_view)
    home = Path.home()
    plugin_id = getpass.getuser() + ".lock"
    target = home / ".config/omarchy/plugins" / plugin_id
    if target.exists():
        manifest = json.loads((target / "manifest.json").read_text())
        if manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.lock":
            raise ValueError(f"{target} is not a clone of omarchy.lock; leaving it untouched.")
        for name, permitted in [
            ("Service.qml", [stock_service, legacy_service, service]),
            ("LockView.qml", [stock_view, legacy_view, view]),
        ]:
            if (target / name).read_text() not in permitted:
                raise ValueError(f"{target / name} has other customizations. Merge them manually; no files changed.")
    for path in [ROOT / "lock-rocinante.png", ROOT / "lock-screen/HandTerminal.qml"]:
        if not path.is_file():
            raise ValueError(f"Missing required asset: {path}")
    if args.check:
        print("Compatible Omarchy lock screen; existing customizations recognized. No files changed.")
        return
    status = json.loads(shell("lock", "status"))
    if status.get("locked") or status.get("requested") or status.get("secure"):
        raise ValueError("Unlock your session before installing the lock-screen visuals.")
    if not target.exists():
        subprocess.run(["omarchy", "plugin", "clone", "omarchy.lock"], check=True)
    backup = home / ".local/state/omarchy/backups" / ("expanse-lock-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    shutil.copytree(target, backup)
    for name, text in [("Service.qml", service), ("LockView.qml", view)]:
        temporary = target / (name + ".new")
        temporary.write_text(text)
        temporary.replace(target / name)
    shutil.copy2(ROOT / "lock-screen/HandTerminal.qml", target / "HandTerminal.qml")
    theme = home / ".config/omarchy/themes/expanse"
    theme.mkdir(parents=True, exist_ok=True)
    if (ROOT / "lock-rocinante.png").resolve() != (theme / "lock-rocinante.png").resolve():
        shutil.copy2(ROOT / "lock-rocinante.png", theme / "lock-rocinante.png")
    current = home / ".local/state/omarchy/current"
    current_name = current / "theme.name"
    if current_name.is_file() and current_name.read_text().strip() == "expanse":
        shutil.copy2(ROOT / "lock-rocinante.png", current / "theme/lock-rocinante.png")
    subprocess.run(["omarchy-shell", "shell", "rescanPlugins"], check=True)
    subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
    print(f"Installed Expanse lock-screen visuals. Backup: {backup}")
    print("Activate while unlocked: omarchy restart shell")
    print(f"Restore stock visuals: omarchy plugin disable {plugin_id}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
