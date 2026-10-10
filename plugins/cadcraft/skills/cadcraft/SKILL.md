---
name: cadcraft
description: >-
  Draft 2D CAD drawings with cadcraft-cli (headless CADCraft, an AutoCAD-style drafting app): draw
  lines, polylines, circles, text, layers, dimensions, hatches and blocks, modify by handle, query
  entities, and convert DXF/DWG to SVG/PNG/PDF. Use for creating, editing, inspecting, converting or
  batch-plotting DXF/DWG drawings.
---

# cadcraft-cli

## Setup

`cadcraft-cli` and `cadcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
cadcraft-cli --version || cadcraft-install   # install the latest release if it's missing
cadcraft-install --check                     # exit 0 up to date, 1 missing, 3 update available
```

If `cadcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Find commands

Every drafting action is a command with an id, aliases and a params signature. Look them up; don't guess.

```bash
cadcraft-cli commands dim          # JSON list filtered by text: id, aliases, menu, params
cadcraft-cli info drawing.dxf      # JSON: entity counts, layers, blocks, dim/text styles, extents
```

In a signature `?` marks optional fields, `|` separates alternative forms, points are `[x,y]`,
angles are degrees and entities are referenced by hex handle strings like `"101"`. Commands whose
`handles` is optional act on the current selection.

## Create a drawing

`run` opens a file (or starts a new mm drawing with `--metric`), runs each `--cmd 'id {json}'`
in order and prints one JSON result per command (new handles, counts). `--save` writes DXF.

```bash
cadcraft-cli run --metric \
  --cmd 'layer.new {"name":"Outline","color":"white","current":true}' \
  --cmd 'rectang {"p1":[0,0],"p2":[100,60]}' \
  --cmd 'circle {"center":[50,30],"radius":15}' \
  --cmd 'layer.new {"name":"Dims","color":"cyan","current":true}' \
  --cmd 'dimlinear {"p1":[0,0],"p2":[100,0],"at":[50,-12]}' \
  --cmd 'dimlinear {"p1":[100,0],"p2":[100,60],"at":[115,30]}' \
  --cmd 'text {"at":[0,70],"text":"PLATE 100x60","height":5}' \
  --save plate.dxf --export plate.png
cadcraft-cli run --metric --script 'LINE 0,0 @40,0 @0,20 C\nCIRCLE 20,10 5\n' --save tri.dxf  # command-line typing
cadcraft-cli run --metric --script-file draw.scr --save out.dxf   # .scr file, one command per line
cadcraft-cli sample bracket bracket.dxf     # sample part drawing (also: floorplan; .dxf .dwg .svg .png)
```

## Edit an existing drawing

Get handles first, then edit by handle or by selection.

```bash
cadcraft-cli run plate.dxf --cmd 'entities {"type":"Circle"}'   # handles + geometry; also layer, window, limit
cadcraft-cli run plate.dxf \
  --cmd 'offset {"handle":"101","distance":5,"side":[50,30]}' \
  --cmd 'dimdiameter {"handle":"101","at":[75,50]}' \
  --cmd 'layer.new {"name":"Hatch","color":"8","current":true}' \
  --cmd 'hatch {"points":[[5,5]],"pattern":"ANSI31","scale":1}' \
  --cmd 'properties.set {"handles":["104"],"color":"red","height":6}' \
  --cmd 'move {"handles":["104"],"delta":[10,0]}' \
  --cmd 'layer.set {"name":"Dims","color":"green"}' \
  --save plate2.dxf
cadcraft-cli run t.dxf --cmd 'fillet {"h1":"100","p1":[10,0],"h2":"101","p2":[0,10],"radius":5}' \
  --cmd 'trim {"handle":"102","pick":[25,-5],"edges":["100"]}' --save t2.dxf   # pick = the part to cut off
cadcraft-cli run bracket.dxf --cmd 'qselect {"type":"Circle"}' --cmd 'erase {}' \
  --cmd 'layer.set {"name":"Center","on":false}' --save edited.dxf
```

Handles of objects created in the same run are printed but not known in advance; select by window
instead, or split into two runs. Blocks and arrays work on the selection:

```bash
cadcraft-cli run --metric \
  --cmd 'circle {"center":[0,0],"radius":3}' --cmd 'line {"points":[[-4,0],[4,0]]}' \
  --cmd 'select {"window":[[-5,-5],[5,5]]}' --cmd 'block {"name":"BOLT","base":[0,0]}' \
  --cmd 'insert {"name":"BOLT","at":[40,0],"scale":2,"rotation":45}' \
  --cmd 'rectang {"p1":[10,10],"p2":[14,14]}' --cmd 'select {"window":[[9,9],[15,15]]}' \
  --cmd 'arrayrect {"rows":2,"cols":3,"rowSpacing":10,"colSpacing":10}' \
  --cmd 'selectall' --cmd 'move {"delta":[100,0]}' --save blocks.dxf
```

## Convert and export

```bash
cadcraft-cli convert plan.dwg plan.dxf       # DWG in; out: .dxf .dwg .svg .png .pdf
cadcraft-cli convert plate2.dxf plate2.pdf   # image/PDF output fits the drawing extents
cadcraft-cli convert plate2.dxf plate2.svg   # or .png (2400x1600)
cadcraft-cli run plate2.dxf --cmd 'saveas {"path":"plate2.dwg","format":"dwg"}'
cadcraft-cli run plate2.dxf --cmd 'exportpdf {"path":"a4.pdf","layout":"Model","paper":"A4","landscape":true,"fit":true}'
for f in *.dxf; do cadcraft-cli convert "$f" "${f%.dxf}.pdf"; done   # batch plot
```

## Check results

```bash
cadcraft-cli info plate2.dxf                 # counts per type, layers (on/frozen/colour), extents
cadcraft-cli run plate2.dxf --export check.png   # 2400x1600 PNG on a dark background
```

Export a PNG and view it to check geometry, layers and dimension placement.
