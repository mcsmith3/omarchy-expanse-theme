# Rocinante About screen

The optional About integration uses the exact Rocinante Unicode/Braille emblem
from the maintainer's About screen. It is 54 columns wide and 22 rows tall.
Omarchy's Fastfetch layout supplies live hardware, software, age, uptime, and
update information beside it. No machine-specific system information is bundled.
The logo and system labels use the active terminal palette.

```sh
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py --check
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py
omarchy launch about
```

Installation registers `50-expanse-about` with Omarchy's `theme-set` hook and
applies it immediately if Expanse is active. Switching away restores your earlier
About branding. If the Rocinante artwork was already active before installation,
the stock Omarchy logo is used for other themes. Existing files are backed up
under `~/.local/state/omarchy/backups/expanse-about-*`.

Manual branding edits are preserved when switching away. Reinstall after updating
the theme to refresh the hook and its installed artwork. Close and reopen About
to see a changed logo. No shell restart is needed.

The integration uses the normal Omarchy Fastfetch configuration, which reads
`~/.config/omarchy/branding/about.txt`. If you use a custom Fastfetch config, its
logo source must point there to display the artwork.

Remove the integration with:

```sh
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py --uninstall
```

This restores the earlier branding if the installed logo remains unchanged and
removes the hook. Backups remain available.
