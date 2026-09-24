# Optional window transparency

The theme’s translucent shell surfaces work through the standard installer.
For subtle window transparency and blur as well, add this block to your personal
`~/.config/hypr/looknfeel.lua` after backing up that file. Review the block first;
it is local Hyprland configuration, not part of the theme installation.

```lua
-- Expanse only; other themes keep their own window styling.
local expanse_theme_file = io.open(os.getenv("HOME") .. "/.local/state/omarchy/current/theme.name", "r")
local expanse_theme_name = expanse_theme_file and expanse_theme_file:read("*l")
if expanse_theme_file then expanse_theme_file:close() end

if expanse_theme_name == "expanse" then
  o.window({ tag = "default-opacity" }, { opacity = "0.96 0.93 1.0" })
  hl.config({
    decoration = {
      blur = { enabled = true, size = 3, passes = 1 },
    },
  })
end
```

Reload and check for errors:

```sh
hyprctl reload
hyprctl configerrors
```

This uses Omarchy’s `default-opacity` tag, preserving its app-specific exceptions
for browsers, media applications, and other excluded windows. The three opacity
values apply to focused, unfocused, and fullscreen windows. Window opacity also
affects the text inside those windows; shell background opacity does not.

Remove this block and reload to return to the theme’s standard window behavior.
Do not edit generated files under `~/.local/state/omarchy/current/theme/`.
