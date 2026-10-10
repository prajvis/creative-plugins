---
name: effectcraft
description: >-
  Build and render motion graphics with effectcraft-cli (headless EffectCraft, an After Effects-style
  compositor): compositions, text/shape/solid/footage layers, keyframes, expressions, effects, masks,
  scripting, and export to H.264/ProRes/WebM/GIF/PNG sequences or Lottie. Use for animated titles,
  lower thirds, motion graphics, compositing footage or rendering .ecproj projects.
---

# effectcraft-cli

## Setup

`effectcraft-cli` and `effectcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
effectcraft-cli --version || effectcraft-install   # install the latest release if it's missing
effectcraft-install --check                       # exit 0 up to date, 1 missing, 3 update available
```

If `effectcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Find commands and properties

Every action is an engine command with an id and JSON params. Look them up; don't guess.

```bash
effectcraft-cli commands --filter layer.new                    # id, label, shortcut, params doc (--json too)
effectcraft-cli exec effect.list '{"filter":"glow"}' --json     # effect names, param ids, defaults
effectcraft-cli info p.ecproj                                   # items, active comp, layers (#n, id, name)
effectcraft-cli props Main Title p.ecproj                       # a layer's property paths and values
```

Pass the project file last; add `--save` (or `--save-as F.ecproj`) to keep changes. `--empty` starts
a blank project (with no project file the demo project loads). Comps: id or name. Layers: id, `#n`
(1 = top) or name. Times in seconds. Unknown param keys fail with the accepted list.

## Build a composition

`run` executes `<id> <json>` pairs in order. Name layers when you create them.

```bash
effectcraft-cli run \
  comp.new '{"name":"Main","width":640,"height":360,"frameRate":24,"duration":2,"background":"#202040"}' \
  layer.newSolid '{"name":"BG","color":"#203060"}' \
  layer.newText '{"text":"Hello","name":"Title","size":72,"fill":"#ffffff"}' \
  layer.newShape '{"kind":"ellipse","name":"Dot","size":[80,80],"fill":"#ff6040","position":[100,280]}' \
  --empty --save-as p.ecproj --json
effectcraft-cli exec file.import '{"paths":["logo.png","clip.mp4"]}' p.ecproj --save
effectcraft-cli run layer.addItem '{"item":"clip.mp4","time":0.5,"position":[480,120]}' \
  layer.timing '{"layers":["Title"],"start":0.25}' p.ecproj --save
```

Also: `layer.newNull`, `layer.setText`, `layer.addMask` (`{"layer":"Plate","shape":"ellipse","rect":[x,y,w,h]}`),
`layer.setParent` (`{"layers":["Plate"],"parent":"Ctrl"}`), `layer.setBlendMode`, `layer.style.dropShadow`.

## Animate and add effects

```bash
effectcraft-cli set Main Dot transform/position '[100,280]' --time 0 p.ecproj --save      # keyframe
effectcraft-cli set Main Dot transform/position '[540,280]' --time 1.5 p.ecproj --save
effectcraft-cli set Main Title transform/rotation 0 --expression 'time*45' p.ecproj --save
effectcraft-cli run keys.select '{"keys":[{"layer":"Dot","path":"transform/position","time":0},{"layer":"Dot","path":"transform/position","time":1.5}]}' \
  keys.easyEase '{}' p.ecproj --save
effectcraft-cli run effect.apply '{"effect":"Glow","layers":["Title"]}' \
  prop.set '{"layer":"Title","path":"effects/#1/radius","value":30}' p.ecproj --save
effectcraft-cli get Main Dot transform/position --time 0.75 p.ecproj --json   # value, keys, evaluated
```

Inside `run`, key with `prop.addKey '{"layer":"Dot","path":"transform/opacity","time":1,"value":0}'`.
Key times are layer time: subtract the layer's start if it was moved with `layer.timing`.
`effect.apply` returns the instance path (`effects/#n`); param ids come from `effect.list`.

## Batch and scripts

`engine.batch` is one undo step; `"$N.layer"` is step N's result.

```bash
effectcraft-cli exec engine.batch --params '{"steps":[{"command":"comp.new","params":{"name":"Card","width":480,"height":270,"duration":1}},{"command":"layer.newSolid","params":{"name":"Plate","color":"#ffcc00"}},{"command":"layer.addMask","params":{"layer":"$2.layer","shape":"ellipse","rect":[90,35,300,200]}}]}' --empty --save-as card.ecproj
effectcraft-cli script anim.jsx card.ecproj --save    # After Effects-style JavaScript (app.project, comp.layers.addText...)
effectcraft-cli script --eval 'app.project.activeItem.numLayers' card.ecproj
```

## Render and export

```bash
effectcraft-cli render-frame --comp Main --time 0.75 --out f.png p.ecproj   # also --max-side 320, --transparent
effectcraft-cli render --comp Main --out out.mp4 --end 1 p.ecproj            # H.264
effectcraft-cli render --comp Main --out out.gif --format gif --resolution half p.ecproj
effectcraft-cli render --comp Card --out card.mov --format prores --prores 4444 --channels rgba card.ecproj
effectcraft-cli render --comp Card --out card.webm --format webm card.ecproj
effectcraft-cli render --comp Main --out 'seq_[###].png' --format png --start 0 --end 0.25 p.ecproj
effectcraft-cli exec file.exportLottie '{"comp":"Main","path":"main.json"}' p.ecproj --json
effectcraft-cli run renderQueue.add '{"comp":"Main","format":"h264","output":"q.mp4"}' p.ecproj --save
effectcraft-cli render --queue p.ecproj                                      # renders every queued item
```

## Check results

Render a frame with `render-frame` and view the PNG. The last frame sits one frame before the
duration; a time equal to the duration renders empty. Read values back with `get` (`evaluated` is
an expression's result) and the layer stack with `info`.
