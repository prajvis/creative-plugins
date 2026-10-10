---
name: designcraft
description: >-
  Lay out documents with designcraft-cli (headless DesignCraft, an InDesign-style page layout app):
  pages, text and graphic frames, threaded text, paragraph styles, parent pages, tables, TOC, data
  merge, packaging, and export to PDF/PNG/JPEG/IDML/EPUB/HTML. Use for building or editing
  .designcraft/.idml layouts, flyers, catalogues, mail-merged cards, or rendering pages to PDF/PNG.
---

# designcraft-cli

## Setup

`designcraft-cli` and `designcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
designcraft-cli --version || designcraft-install   # install the latest release if it's missing
designcraft-install --check                       # exit 0 up to date, 1 missing, 3 update available
```

If `designcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Find commands

Every action is a command with an id and a params doc. Look ids up; don't guess.

```bash
designcraft-cli commands style.paragraph          # JSON: id, label, menu, params, enabled
designcraft-cli describe file.exportPdf           # one command's params
designcraft-cli run --in doc.designcraft --cmd document.inspect   # pages, spreads, items, stories, styles
```

Units are points; `rect` is `[x0,y0,x1,y1]` in spread coordinates (`document.inspect` gives each
page's bounds; with facing pages a right-hand page starts at x = page width). Commands that act on
the selection need `selection.set` (objects) or `text.select` (text) first.

## Build a layout (script)

`script` runs one `command.id {json}` per line on a blank Letter document (or `--in FILE`).
`"$N.key"` is a value from step N's result (0-based). Text frames need `"content":"text"`.

```bash
cat > flyer.dcs <<'DCS'
file.new {"width":432,"height":648,"pages":1,"facingPages":false,"margins":36}
swatch.create {"name":"Brand","color":"#1b6ca8"}
style.paragraph.create {"name":"Head","para":{"align":"center"},"chars":{"size":28,"fill":"Brand"}}
frame.create {"rect":[36,36,396,100],"content":"text","text":"Spring Sale"}
selection.set {"ids":["$3.id"]}
style.paragraph.apply {"name":"Head"}
frame.create {"rect":[36,110,396,300],"content":"graphic"}
file.place {"path":"photo.png","frame":"$6.id"}
object.fit {"mode":"fillProportionally"}
frame.create {"rect":[36,320,396,600],"content":"text","text":"Body copy."}
selection.set {"ids":["$9.id"]}
object.textFrameOptions {"columns":2,"gutter":12}
text.select {"story":"$9.story","anchor":0,"focus":4}
type.char {"attrs":{"size":14,"fill":"Brand"}}
DCS
designcraft-cli script flyer.dcs --save flyer.designcraft --export flyer.pdf --export flyer.png
```

Output is JSON `{completed, results}`; a failed step adds `failedIndex`/`error` and exits non-zero
(`--keep-going` continues). `script --export` PNGs render at 2x.

## Text, pages, parents, TOC

```bash
cat > book.dcs <<'DCS'
file.new {"preset":"A4","pages":2,"facingPages":true,"margins":{"top":48,"bottom":48,"inside":54,"outside":36}}
layout.parents.new {"name":"Chapter"}
layout.pages.insert {"count":2,"parent":"B"}
layout.pages.applyParent {"pages":[0],"parent":null}
style.paragraph.create {"name":"H1","chars":{"size":24}}
frame.create {"rect":[54,48,559,100],"content":"text","text":"Introduction"}
selection.set {"ids":["$5.id"]}
style.paragraph.apply {"name":"H1"}
frame.create {"spread":1,"rect":[36,48,559,780]}
file.place {"path":"chapter.txt","autoflow":true}
find.change {"find":"Lorem","change":"Ipsum"}
toc.generate {"styles":["H1"],"page":1}
DCS
designcraft-cli script book.dcs --save book.designcraft     # autoflow adds pages of threaded frames
```

`layout.pages.*` take 0-based page indexes; `layout.pages.delete {"pages":[i]}` removes spare pages.
Also: `story.setText {story,text}`, `story.get {story}`, `table.convertFromText` on selected text.

## Data merge

Mark placeholders in a template, then merge a CSV into a new document (one record per page).
Pass the CSV as `./file.csv` or an absolute path so image fields resolve next to it.

```bash
cat > card.dcs <<'DCS'
file.new {"width":288,"height":180,"pages":1,"facingPages":false,"margins":12}
frame.create {"rect":[12,12,180,40],"content":"text","text":""}
frame.create {"rect":[190,12,276,98],"content":"graphic"}
data.source.select {"path":"./people.csv","name":"people.csv"}
data.placeholder.add {"field":"name","story":"$1.story","at":0}
data.placeholder.add {"field":"photo","role":"image","item":"$2.id"}
DCS
designcraft-cli script card.dcs --save card.designcraft
echo 'data.merge {"path":"./people.csv"}' | designcraft-cli script - --in card.designcraft --save merged.designcraft --export merged.pdf
```

Check `missingImages` and `oversetStories` in the merge result.

## Export and convert

```bash
designcraft-cli run --in flyer.designcraft --export out.pdf --export out.idml --export out.epub
designcraft-cli run --in out.idml --scale 2 --export page.png   # --scale before --export; also .jpg
designcraft-cli run --in book.designcraft --page 1 --export p2.png   # one page, 0-based (page 2)
designcraft-cli run --in book.designcraft --all-pages pages/        # pages/page-001.png ...
designcraft-cli run --in book.designcraft --pdf-options '{"pages":"1-2","standard":"x4"}' --export print.pdf
designcraft-cli run --in book.designcraft --cmd 'file.exportPdf={"path":"bleed.pdf","bleed":true,"marks":true}'
designcraft-cli run --in flyer.designcraft --cmd 'file.exportHtml={"path":"flyer.html"}'
designcraft-cli run --in flyer.designcraft --cmd 'file.package={"dir":"pkg","pdf":true}'  # doc, Links/, IDML, PDF, report
```

`run` takes repeated `--cmd ID=JSON` too; save with `--cmd 'file.saveAs={"path":"x.designcraft"}'`.

## Check results

```bash
designcraft-cli run --in book.designcraft --cmd preflight.run --cmd links.list --cmd font.list
```

`document.inspect` marks stories whose text doesn't fit with `overset: true`. Render a PNG and view
it to check the layout.
