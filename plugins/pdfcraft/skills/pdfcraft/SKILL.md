---
name: pdfcraft
description: >-
  Work on PDFs with pdfcraft-cli (headless PdfCraft, an Acrobat-style PDF editor): merge, split,
  reorder/rotate/delete pages, extract text and images, render pages, fill forms, passwords,
  redaction, watermarks, headers/footers, metadata, compression, OCR and export to Word/HTML/images.
  Use for organizing, inspecting, protecting, converting or batch-processing PDF files.
---

# pdfcraft-cli

## Setup

`pdfcraft-cli` and `pdfcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
pdfcraft-cli --version || pdfcraft-install   # install the latest release if it's missing
pdfcraft-install --check                     # exit 0 up to date, 1 missing, 3 update available
```

If `pdfcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Inspect, render, text

```bash
pdfcraft-cli info in.pdf                          # pages, page size, title/author, fields, bookmarks as JSON
pdfcraft-cli info locked.pdf --password open123   # encrypted files (text also takes --password)
pdfcraft-cli text in.pdf --page 2                 # reading-order text; omit --page for all (form feed between pages)
pdfcraft-cli render in.pdf --page 1 --dpi 150 --out p1.png   # .png .jpg .tif
pdfcraft-cli check a.pdf b.pdf --json check.json  # open+render health check per file
```

## Organize pages

```bash
pdfcraft-cli combine a.pdf b.pdf --out merged.pdf
pdfcraft-cli extract in.pdf --pages 1,3 --out some.pdf
pdfcraft-cli split in.pdf --every 2 --out-dir parts      # parts/in-p1-2.pdf, ... (or --before 2,5)
pdfcraft-cli edit in.pdf --out out.pdf --rotate 1,3:90 --delete 2 --insert-blank 1 \
  --title "Q3 Report" --author "Ann"                     # page numbers refer to in.pdf
pdfcraft-cli edit in.pdf --out out.pdf --move 3:1        # page 3 becomes page 1
```

## Everything else: tools and scripts

All other jobs are automation tools with JSON Schemas. Look names and params up; don't guess.

```bash
pdfcraft-cli tools | grep -o '"name": "[a-z_]*"'          # all tool names
pdfcraft-cli tools | python3 -c 'import json,sys; t={x["name"]:x for x in json.load(sys.stdin)}; print(json.dumps(t["doc_watermark"], indent=1))'
pdfcraft-cli run doc_create_multiple 'paths=["scan.png","in.pdf"]' out=all.pdf   # one-off: key=value, values parse as JSON
```

A one-off `run` is a fresh session, so tools that take `doc` need a script. A script runs steps in one
session: `doc_open`/`doc_create` give ids 1, 2, ... in order; edits stay in memory until `doc_save`
with `path`. It stops at the first failing step (exit 1). Coordinates are points from the page's top-left.

```bash
cat > steps.json <<'JSON'
[{"tool":"doc_open","args":{"path":"in.pdf"}},
 {"tool":"doc_watermark","args":{"doc":1,"text":"DRAFT","opacity":0.3}},
 {"tool":"doc_header_footer","args":{"doc":1,"header_right":"ACME","footer_center":"<<Page 1 of n>>"}},
 {"tool":"bookmark_add","args":{"doc":1,"title":"Start","page":1}},
 {"tool":"page_add_text","args":{"doc":1,"page":1,"text":"Approved","at":[72,700],"size":18}},
 {"tool":"page_add_image","args":{"doc":1,"page":2,"path":"logo.png","rect":[72,200,272,350]}},
 {"tool":"comment_add","args":{"doc":1,"page":1,"type":"highlight","find":"total due"}},
 {"tool":"redact_mark","args":{"doc":1,"find":"42 EUR"}},
 {"tool":"redact_apply","args":{"doc":1}},
 {"tool":"doc_save","args":{"doc":1,"path":"out.pdf"}},
 {"tool":"page_render","args":{"doc":1,"page":1,"dpi":72},"out":"check.png"},
 {"tool":"doc_export_images","args":{"doc":1,"folder":"pages","format":"png","dpi":100}},
 {"tool":"doc_export_all_images","args":{"doc":1,"folder":"imgs"}},
 {"tool":"doc_export_office","args":{"doc":1,"path":"out.docx"}},
 {"tool":"doc_reduce","args":{"doc":1,"path":"small.pdf"}}]
JSON
pdfcraft-cli run --script steps.json         # each step prints its JSON result
```

Other steps, same shape (add `"doc":1`; finish with `doc_save`):
- Metadata: `doc_set_info` `{"key":"Subject","value":"Q3"}`.
- Passwords: `doc_protect` `{"open_password":"open123","permissions_password":"owner456","printing":"low","copy":false}`.
  To remove: `doc_open` `{"path":"locked.pdf","password":"owner456"}`, then `doc_unprotect`.
- Forms: `form_fields` lists names/types; `form_fill` `{"values":{"name":"Ada","agree":true,"plan":"Pro"}}`;
  `doc_export_data` `{"path":"data.xfdf"}`; `doc_flatten` bakes fields and comments into the page.
- New PDFs: `doc_create` `{"from":"blank","pages":3}`, `{"from":"images","paths":["a.png"]}` or `{"from":"text","text":"..."}`.
- Size/export: `doc_optimize` `{"path":"opt.pdf","color":{"ppi":72,"quality":50}}`; `doc_export_office` to
  `.docx`, `.html` or `.rtf`; `doc_export_text` `{"path":"out.txt"}`.
- Search/sanitize: `text_find` `{"query":"invoice"}`; `doc_remove_hidden` strips metadata, comments, scripts etc.
- OCR for scans: `ocr_recognize` adds searchable text. `pdfcraft-install` puts the OCR models in
  `bin/models` on Linux. Check `pdfcraft-cli run ocr_status` reports `"available": true` first; if
  not, run `pdfcraft-install --force`, and if it is still unavailable tell the user.

## Check results

`pdfcraft-cli info out.pdf` for page count, metadata, `encrypted`, `fields`; `pdfcraft-cli text out.pdf`
to confirm text was added or redacted; render a page to PNG and view it to check visual edits.
