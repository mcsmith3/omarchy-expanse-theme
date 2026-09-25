# Rocinante hand-terminal lock screen

The optional lock screen runs in **Omarchy Shell / Quickshell**. It does not
install Hyprlock or change your lock keybinding, idle timer, PAM configuration,
or fingerprint enrollment.

## Install

Install/update the theme through Omarchy first. With an unlocked desktop and
Omarchy Shell running:

```sh
python3 ~/.config/omarchy/themes/expanse/scripts/install-lock-screen.py --check
python3 ~/.config/omarchy/themes/expanse/scripts/install-lock-screen.py
omarchy restart shell
```

If working from a Git checkout instead, run `python3 scripts/install-lock-screen.py`
from that checkout after installing the theme.

The installer uses the supported `omarchy plugin clone omarchy.lock` command
when you do not already have a local clone. It makes a timestamped backup under
`~/.local/state/omarchy/backups/` and adds the visuals to
`~/.config/omarchy/plugins/<username>.lock/`. It checks the current installed
Omarchy QML structure before editing and refuses to overwrite unrelated local
customizations. `--check` performs these checks without changing files or
contacting the running shell. Python 3 and the Omarchy plugin CLI are required.

Prepared and previewed against the Omarchy Shell lock plugin installed on
2026-09-25. Compatibility is checked by source structure, not just a version
number. If a later version fails the check, do not bypass it; adapt the visual
integration to that version. The installer patches your installed service and
view, so this repository does not ship a frozen copy of the authentication
implementation. A local clone nevertheless remains a snapshot until refreshed;
review relevant upstream lock-plugin updates before reinstalling the visuals.

Omarchy intentionally retains its lock service during ordinary hot reloads.
The shell restart activates changes; it briefly reloads the bar as well.

## Appearance and behavior

- `lock-rocinante.png` selects the Rocinante artwork and hand-terminal layout.
- A theme with only `lock-background.png` uses that image with the normal field.
- With neither file, the current desktop wallpaper uses the original blur and field.
- The terminal scales down on smaller screens. It retains masked input,
  Enter-to-submit, Escape/Ctrl+U clearing, and the fingerprint indicator.
- The round button at the bottom submits the same password field as Enter.
- “Checking…” and authentication errors appear in the real input area; the
  identity heading also changes to reflect checking or failure.
- The etched navigation and signal graphics are decorative, not live telemetry.

The image is kept outside `backgrounds/`, so desktop wallpaper cycling does not
select it. Omarchy stages it with Expanse on theme changes. Theme changes take
effect the next time the lock screen opens.

## Preview and remove

To inspect the layout without locking your desktop:

```sh
omarchy-shell lock preview
```

Click to dismiss the preview, or run `omarchy-shell lock hidePreview`. Preview
mode deliberately disables password entry; it does not test authentication.

Restore the stock lock screen (replace `<username>` with your login name):

```sh
omarchy plugin disable <username>.lock
```

The clone and its backups remain available. The theme's desktop settings are
unaffected. Updating the theme alone does not rewrite an installed plugin clone;
run the optional installer and restart the shell to apply interface updates.

References and generation details are recorded in [ARTWORK.md](../ARTWORK.md).
