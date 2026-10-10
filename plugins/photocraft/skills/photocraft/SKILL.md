---
name: photocraft
description: >-
  Edit images with photocraft-cli (headless PhotoCraft, a Photoshop-style editor): crop, resize,
  tone and colour adjustments, filters, layers, masks, selections, compositing, PSD/.pcraft
  documents and export to PNG/JPEG/TIFF/WebP/EXR. Use for editing, retouching, compositing,
  converting or batch-processing images.
---

# photocraft-cli

## Setup

`photocraft-cli` and `photocraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
photocraft-cli --version || photocraft-install   # install the latest release if it's missing
photocraft-install --check                       # exit 0 up to date, 1 missing, 3 update available
```

If `photocraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Find commands

Every editor action is an engine command with an id and typed params. Look ids up; don't guess.

```bash
photocraft-cli commands --filter crop                    # id, label, menu path
photocraft-cli commands --json --filter brightnessContrast  # includes the params signature
photocraft-cli info photo.psd --compact                  # size, mode, depth, layer tree as JSON
```

A params signature like `{"brightness":-150..150=0,"contrast":-50..100=0}` gives name, range and
default. Commands listed with `"enabled": false` need an open document (some also a selection).

Families: `image.*` (crop, imageSize, canvasSize, autoTone, adjustments.*), `layer.*` (layers,
groups, `layer.layerMask.*`, adjustment layers), `select.*` (`select.all`, `select.subject`),
`filter.*`, `edit.*` (`edit.fill`, `edit.stroke`), `file.placeEmbedded` (add another image as a
layer), `type.*`.

## Edit

`run` opens a file, runs commands in order and saves. Each `--params` applies to the `--cmd` before it.

```bash
photocraft-cli run in.jpg \
  --cmd image.crop --params '{"x":50,"y":40,"width":300,"height":200}' \
  --cmd image.adjustments.brightnessContrast --params '{"brightness":30,"contrast":10}' \
  --out work.psd
photocraft-cli run in.png --cmd image.adjustments.invert --out inverted.png
photocraft-cli convert work.psd final.jpg --quality 90      # .pcraft .psd .png .jpg .tif .webp .exr
```

Save a `.psd`/`.pcraft` when later changes are likely, then `convert` it to the deliverable.

## Batch

```bash
photocraft-cli batch --actions actions.json --in ./originals --out ./edited --format jpg --quality 90
# actions.json: [["image.autoTone", {}], ["image.imageSize", {"width": 1600}]]
```

`imageSize` with only `width` keeps the aspect ratio. `--out` must differ from `--in` unless you pass
`--in-place`. Inputs that share a name (`a.jpg`, `a.png`) collide when converted to one format; the
second one fails. Recorded actions and droplets work too (`droplet <file.pcdroplet> <files>...`).

## Long sessions

`photocraft-cli serve` keeps one document open and answers JSON lines on stdio (`doc.open`,
`engine.execute`, `doc.render`, `doc.save`, ...), so many dependent steps don't reopen the file.
Don't use `photocraft-cli mcp`: MCP servers launched from a plugin aren't supported here. Call
`photocraft-cli` directly. `photocraft-cli <subcommand> --help`
prints the full reference.

Render or export a PNG/JPEG and view it to check an edit.
