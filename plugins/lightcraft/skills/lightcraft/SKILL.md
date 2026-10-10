---
name: lightcraft
description: >-
  Develop and export photos with lightcraft-cli (headless LightCraft, a Lightroom-style raw
  developer): exposure, contrast, highlights/shadows, white balance, curves, auto settings,
  presets, HDR and panorama merges, resized exports. Use for colour-correcting, toning, raw
  development or bulk export of photos.
---

# lightcraft-cli

## Setup

`lightcraft-cli` and `lightcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
lightcraft-cli --version || lightcraft-install   # install the latest release if it's missing
lightcraft-install --check                       # exit 0 up to date, 1 missing, 3 update available
```

If `lightcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

On headless Linux it may print `XDG_RUNTIME_DIR is invalid or not set`; harmless. Set
`XDG_RUNTIME_DIR` to a private (mode 700) temp dir to silence it.

## Find controls and commands

```bash
lightcraft-cli controls                          # develop controls with ranges and defaults
lightcraft-cli commands                          # every command id with its parameters
lightcraft-cli --help                            # full reference
lightcraft-cli run --import in.jpg presets.list  # built-in presets, e.g. lc.warm-glow, lc.teal-orange
```

Control ids include `light.exposure` (-5..5), `light.contrast`, `light.highlights`,
`light.shadows`, `light.whites`, `light.blacks`, `wb.temp`, `wb.tint`, `curve.*`.

## Develop one file

```bash
lightcraft-cli render in.jpg -o out.jpg --set light.exposure=0.5 --set light.shadows=30 --size 2048
lightcraft-cli render in.jpg -o out.jpg --preset lc.warm-glow --quality 90
```

Output format comes from the extension (jpg, png, tif, webp, avif, dng). `--size` is the long edge in
pixels and doesn't upscale. `--settings file.json` merges partial develop settings; `--opt KEY=VALUE`
passes any `app.export` option (e.g. `--opt colorSpace=displayP3`).

## Chain commands

```bash
lightcraft-cli run --import in.jpg \
  develop.auto \
  develop.set control=light.exposure value=0.3 \
  app.export path=/abs/path/out.jpg longEdge=1600
```

Each word without `=` starts a new command; each prints one JSON line with `ok`. `develop.auto` sets
exposure and other controls itself, so put manual `develop.set` calls after it. `--import` takes files
or folders and can repeat; `--library DIR` keeps a persistent library; `--keep-going` continues past
failures.

## Merge

```bash
lightcraft-cli merge hdr a.dng b.dng c.dng          # writes a-HDR.dng next to the first file
lightcraft-cli merge panorama *.jpg --preview p.png # preview only, writes nothing next to inputs
```

Options: `--deghost none|low|medium|high`, `--projection auto|spherical|cylindrical|perspective`,
`--auto-crop`, `--fill-edges`. Merge writes next to its inputs.

Don't use `lightcraft-cli mcp`: MCP servers launched from a plugin aren't supported here. Call
`lightcraft-cli` directly.
