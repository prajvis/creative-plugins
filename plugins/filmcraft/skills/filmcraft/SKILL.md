---
name: filmcraft
description: >-
  Edit video with filmcraft-cli (headless FilmCraft, a Premiere-style editor): import media, build
  sequences, cut and trim, apply effects and transitions, render frames and export
  H.264/ProRes/DNxHR/GIF/image sequences/audio. Use for cutting, assembling, trimming,
  re-encoding or exporting video.
---

# filmcraft-cli

## Setup

`filmcraft-cli` and `filmcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
filmcraft-cli --version || filmcraft-install   # install the latest release if it's missing
filmcraft-install --check                      # exit 0 up to date, 1 missing, 3 update available
```

If `filmcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## How calls work

Each call is one headless session. `--project p.fcproj` opens a project first, `--save` writes it
back, `--save-as other.fcproj` writes elsewhere; without them edits are discarded when the call ends.
Output is JSON (`--compact` for one line). Exit status: 0 ok, 1 a command failed, 2 usage error.

```bash
filmcraft-cli help                                # full reference
filmcraft-cli commands razor                      # find command ids
filmcraft-cli describe timeline.razor             # params, and whether it's enabled right now
filmcraft-cli --project p.fcproj inspect project  # bins and items with ids
filmcraft-cli --project p.fcproj inspect sequence # tracks, clips, effects, markers
filmcraft-cli probe input.mp4                     # media info
```

`key=value` arguments parse as JSON when possible (`seconds=3.5`, `items=[1]`), otherwise as strings;
dotted keys nest. Time is in ticks (254016000000 per second); most commands also take `seconds=`,
`frame=` or `timecode=`.

## Basic edit

```bash
filmcraft-cli --compact --save-as edit.fcproj import clip.mp4             # -> {"items":[1],...}
filmcraft-cli --compact --project edit.fcproj --save \
  exec file.newSequence name=Main fromItem=1                              # sequence matching the clip
filmcraft-cli --compact --project edit.fcproj --save exec timeline.razor seconds=2
filmcraft-cli --project edit.fcproj render --seconds 1 --out frame.png   # one Program frame as PNG
filmcraft-cli --project edit.fcproj export out.mp4 --start 0 --end 3     # waits until written
```

- Most editing commands need an open sequence; `no sequence is open` means create or open one.
- Use `file.newSequence ... fromItem=<id>`; `file.newSequenceFromClip` needs a Project-panel selection.
- Several commands in one call: one `{"id": "...", "params": {...}}` per line in a file, then
  `filmcraft-cli --project edit.fcproj --save run steps.jsonl` (stops at the first failure unless
  `--keep-going`; `run -` reads stdin).

## Export

```bash
filmcraft-cli export --list-presets youtube
filmcraft-cli --project edit.fcproj export out --preset "<preset name>" --start 0 --end 10
filmcraft-cli --project edit.fcproj export out.mov --format prores
```

Formats: h264, hevc, prores, dnxhr, apv, mjpeg, mxf-op1a, mxf-opatom, png, tiff, bmp, gif, wav, aiff
(guessed from the extension). `--range entire|inOut|workArea`, or `--start/--end` in seconds.
`--settings` merges ExportSettings JSON over the preset. `--scale 0.5` renders at half size,
`--quality 0-100` for formats that take one, `--no-audio` drops sound. Exports encode on the CPU; run
long ones as a background job.

Don't use `filmcraft-cli mcp`: MCP servers launched from a plugin aren't supported here. Call
`filmcraft-cli` directly.
