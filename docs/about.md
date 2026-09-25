# Rocinante About screen

The optional About integration pairs the Rocinante Unicode/Braille emblem with
a shipboard diagnostics layout. Copper headings, warm peach values, gray rules,
and ochre service labels match the Expanse palette. **REMEMBER THE CANT** sits
beneath the emblem. `rocinante.txt` preserves the original 54-column, 22-row art;
`logo.txt` adds Fastfetch color markers and the motto.

The three panels show live system values with themed labels:

| Panel | Labels |
| --- | --- |
| Ship Systems | Hull, Processing core, Render array, Visual interface, Data banks, Working memory, Reserve memory |
| Flight Software | Operating system, Core, Display control, Command console, Software manifest, Update channel, Livery, Interface font |
| Service Log | Time in service, Current watch, Last maintenance |

Data banks and Working memory include compact usage bars. Data banks shows the
root filesystem. No machine-specific values are bundled; these are Fastfetch
snapshots taken when About opens or redraws.

```sh
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py --check
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py
omarchy launch about
```

Installation registers `50-expanse-about` with Omarchy's `theme-set` hook and
applies it immediately if Expanse is active. Switching away restores your earlier
About branding **and Fastfetch configuration**, including an original config
symlink. If no user Fastfetch config existed, the override is removed so Omarchy's
system defaults take over again. If the Rocinante artwork was already active before installation,
the stock Omarchy logo is used for other themes. Existing files are backed up
under `~/.local/state/omarchy/backups/expanse-about-*`.

Manual edits to either managed file are preserved when switching away. Reinstall after updating
the theme to refresh the hook, artwork, and diagnostics config. This also upgrades
the earlier logo-only installation without replacing its saved original branding.
Close and reopen About
to see a changed logo. No shell restart is needed.

While active, the integration manages `~/.config/fastfetch/config.jsonc` and
`~/.config/omarchy/branding/about.txt`. Omarchy skips its automatic About-window
fitting when a user Fastfetch configuration exists; resize the floating window
if your font or display needs more room. The layout is approximately 120 columns
and 26 rows, with additional width possible for longer hardware names.

Remove the integration with:

```sh
python3 ~/.config/omarchy/themes/expanse/scripts/install-about.py --uninstall
```

This restores each earlier file if its installed version remains unchanged and
removes the hook. Backups remain available.
