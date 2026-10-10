---
name: vectorcraft
description: >-
  Create and edit vector artwork with vectorcraft-cli (headless VectorCraft, an Illustrator-style
  editor): shapes, paths, text, gradients, live effects, Pathfinder, layers, artboards, image trace,
  and conversion between SVG, PDF, AI, EPS, DXF, EMF and PNG/JPEG/TIFF/WebP/PSD. Use for drawing,
  editing, converting, rasterizing or batch-processing vector files.
---

# vectorcraft-cli

## Setup

`vectorcraft-cli` and `vectorcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
vectorcraft-cli --version || vectorcraft-install   # install the latest release if it's missing
vectorcraft-install --check                        # exit 0 up to date, 1 missing, 3 update available
```

If `vectorcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Find commands

Every editor action is a command with an id and a params signature. Look them up; don't guess.

```bash
vectorcraft-cli commands > cmds.json      # catalogue as JSON: id, label, menu, params
python3 -c 'import json;[print(c["id"],c["params"]) for c in json.load(open("cmds.json")) if "shape." in c["id"]]'
vectorcraft-cli run --cmd file.new --cmd effect.list > effects.jsonl   # effect ids, params, defaults
vectorcraft-cli info art.svg              # artboards, units, object counts by kind, fonts, import warnings
```

In a signature like `{x, y, width, height, radius?: pt}`, `?` marks optional and `=` a default.
Units are points (1 px at scale 1); the origin is the first artboard's top-left, y points down.

## Create artwork

`run` starts a new document (or opens `--in FILE`), runs each `--cmd` with the `--params` after it,
then writes every `--export` by extension. One JSON line per step (new objects return `{"id":N}`);
a failing step exits 1 and writes nothing.

```bash
vectorcraft-cli run \
  --cmd file.new --params '{"width":400,"height":300,"units":"Pixels"}' \
  --cmd shape.rectangle --params '{"x":20,"y":20,"width":200,"height":120,"radius":12}' \
  --cmd paint.setFill --params '{"color":"#ff6600"}' \
  --cmd shape.ellipse --params '{"x":200,"y":120,"width":150,"height":150}' \
  --cmd paint.setFill --params '{"color":"#0066ff"}' --cmd stroke.set --params '{"weight":4}' \
  --cmd text.create --params '{"x":30,"y":250,"text":"Hello","size":36,"color":"#222222"}' \
  --export art.vectorcraft --export art.svg --export art.png
```

A new object is selected, so paint, stroke and effect commands after it apply to it. `paint.setFill`
also sets the fill of later new objects; give text its own `color`. Wrapping text: add
`"area":{"width":160,"height":60}` to `text.create`. Gradients, effects and several artboards:

```bash
vectorcraft-cli run --cmd file.new --params '{"width":300,"height":300,"artboards":3}' \
  --cmd shape.star --params '{"cx":150,"cy":150,"radius1":100,"radius2":45,"points":5}' \
  --cmd paint.setFill --params '{"gradient":{"kind":"linear","angle":90,"stops":[{"offset":0,"color":"#ffcc00"},{"offset":1,"color":"#ff3300"}]}}' \
  --cmd effect.apply --params '{"effect":"stylize.dropShadow","params":{"x":5,"y":5,"blur":4}}' \
  --cmd path.create --params '{"d":"M 340 50 L 560 250 L 340 250 Z"}' \
  --cmd shape.polygon --params '{"cx":800,"cy":150,"radius":90,"sides":6}' \
  --cmd object.rotate --params '{"angle":30}' \
  --export sheet.vectorcraft --export sheet.pdf    # artboards sit in a row at x 0, 320, 640; PDF gets 3 pages
```

## Edit an existing file

Get object ids first, then select by id. Pathfinder results get new ids (returned in the output).

```bash
vectorcraft-cli run --in art.vectorcraft --cmd document.find --params '{"kind":"Ellipse"}'  # or {"text":..}, {"name":..}
vectorcraft-cli run --in art.vectorcraft --cmd document.inspect --params '{"depth":2}'      # tree: ids, bounds, fill, stroke
vectorcraft-cli run --in art.vectorcraft \
  --cmd select.set --params '{"ids":[2,3]}' --cmd object.pathfinder.unite \
  --cmd paint.setFill --params '{"color":"#22aa55"}' \
  --cmd text.setText --params '{"id":4,"text":"Hi there"}' \
  --cmd select.set --params '{"ids":[4]}' --cmd type.createOutlines \
  --cmd select.all --cmd object.align --params '{"horizontal":"center","to":"artboard"}' \
  --cmd object.group --cmd object.setProps --params '{"name":"art","opacity":80}' \
  --cmd object.move --params '{"dx":-10,"dy":5}' --cmd object.scale --params '{"sx":90}' \
  --export edited.vectorcraft --export edited.svg
```

`edit.clear {"ids":[..]}` deletes; `layer.new {"name":..,"top":true}` adds a layer for new art.

## Convert and export

Writes .vectorcraft .svg .pdf .ai .eps .dxf .emf .wmf .png .jpg .webp .tif .psd and more; reads
those plus Affinity files and raster images. `warnings` in the JSON result names anything lost.

```bash
vectorcraft-cli convert art.svg art.pdf                              # format from the extension
vectorcraft-cli convert art.pdf art@2x.png --scale 2                 # raster at 2 px per pt
vectorcraft-cli convert art.vectorcraft outlined.svg --outline-text  # text as paths
vectorcraft-cli convert sheet.vectorcraft board2.png --artboard 1    # 0-based artboard
vectorcraft-cli convert sheet.vectorcraft pages.pdf --range 2-3      # 1-based artboards
vectorcraft-cli run --in sheet.vectorcraft --cmd document.export \
  --params '{"path":"board.png","useArtboards":true,"scale":2,"background":"white"}'  # board-Artboard-1.png..-3
for f in in/*.svg; do vectorcraft-cli convert "$f" "out/$(basename "${f%.svg}").pdf"; done  # batch
```

PNG is transparent unless `background` is set; `document.export` also takes `quality` for JPEG.

## Trace or place raster images

```bash
vectorcraft-cli run --in art.png --cmd select.all \
  --cmd imageTrace.make --params '{"preset":"6 Colors"}' --cmd imageTrace.expand --export traced.svg
vectorcraft-cli run --cmd file.new --cmd imageTrace.presets          # preset names and their params
vectorcraft-cli run --in art.vectorcraft --cmd file.place \
  --params '{"path":"photo.png","rect":[0,0,200,150]}' --export placed.pdf   # place into a document
```

## Check results

Run `vectorcraft-cli info` on the output (artboards, object kinds) or `document.inspect` for the tree,
and export a PNG (`vectorcraft-cli convert edited.svg check.png`) and view it.
