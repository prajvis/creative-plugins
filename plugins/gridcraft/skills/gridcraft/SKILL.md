---
name: gridcraft
description: >-
  Build, edit and analyse spreadsheets with gridcraft-cli (headless GridCraft, an Excel-style
  spreadsheet app): read and write cells and formulas, evaluate Excel formulas, format, sort,
  filter, tables, charts, pivot tables, and convert between XLSX, CSV, TSV, JSON, HTML and PDF.
  Use for spreadsheet reports, data cleanup, formula work and workbook conversion.
---

# gridcraft-cli

## Setup

`gridcraft-cli` and `gridcraft-install` live in this plugin's `bin/`, which is on PATH.

```bash
gridcraft-cli --version || gridcraft-install   # install the latest release if it's missing
gridcraft-install --check                      # exit 0 up to date, 1 missing, 3 update available
```

If `gridcraft-install` says `bin/` is read-only, this computer can't install it (on Prajvis only the
agent owner's superuser computer can). Tell the user.

## Look at a workbook

```bash
gridcraft-cli info book.xlsx                    # sheets, used ranges, tables, charts, names
gridcraft-cli cat book.xlsx --range A1:F20      # displayed values as an aligned table
gridcraft-cli cat book.xlsx --sheet Sales --formulas --csv
gridcraft-cli eval '=SUMIF(A2:A7,"North",E2:E7)' --in book.xlsx   # one formula against the file
gridcraft-cli eval '=PMT(5%/12,360,-300000)'    # no file needed
```

Inputs: `.xlsx`, `.xlsm`, `.csv`, `.tsv`, `.txt`, `.json`, plus `.xlsb`/`.ods` data import. A CSV
opens as one sheet named after the file (`sales.csv` → `sales`), not `Sheet1`.

## Find commands and functions

Every edit is a command id with JSON params. Look them up; don't guess.

```bash
gridcraft-cli commands --search chart           # ids with their params
gridcraft-cli commands --json                   # everything, machine-readable
gridcraft-cli functions --search lookup         # supported formula functions
```

Families: `cell.set`, `range.setValues`, `edit.*` (fill, clear), `home.*` (font, fill, borders,
number formats, alignment, rows/columns/sheets, conditional formatting), `data.*` (sort, filter,
remove duplicates, text to columns, validation), `insert.*` (table, chart, pivotTable), `chart.*`,
`sheet.*`, `formulas.*`, `view.*`, `file.*` (`file.exportPdf`).

## Edit

`run` opens `--in` (or a blank workbook), runs each `--cmd 'id={json}'` in order, saves `--out` and
prints `--print` ranges (`used` for the whole used range). It stops at the first failing command.

```bash
gridcraft-cli run --in sales.csv \
  --cmd 'cell.set={"cell":"E1","input":"Revenue"}' \
  --cmd 'cell.set={"cell":"E2","input":"=C2*D2"}' \
  --cmd 'edit.fillDown={"range":"E2:E7"}' \
  --cmd 'home.bold={"range":"A1:E1"}' \
  --cmd 'home.numberFormat={"range":"D2:E7","format":"Currency"}' \
  --cmd 'home.autofitColumnWidth={"cols":"A:E"}' \
  --out report.xlsx --print A1:E7

gridcraft-cli run --cmd 'range.setValues={"range":"A1","values":[["Month","Spend"],["Jan",1200],["Feb",950],["Total","=SUM(B2:B3)"]]}' \
  --cmd 'sheet.rename={"name":"Budget"}' --out budget.xlsx    # new workbook
```

Strings starting with `=` are formulas. Most commands take `range` and an optional `sheet`.

## Analyse and present

```bash
gridcraft-cli run --in report.xlsx \
  --cmd 'data.removeDuplicates={"range":"A1:E7","header":true}' \
  --cmd 'data.sort={"range":"A1:E7","header":true,"keys":[{"column":"E","order":"desc"}]}' \
  --out sorted.xlsx --print used

gridcraft-cli run --in report.xlsx \
  --cmd 'insert.table={"range":"A1:E7","name":"Sales"}' \
  --cmd 'insert.chart={"range":"A1:A7,E1:E7","type":"column","title":"Revenue","at":"G2"}' \
  --cmd 'home.conditionalFormat={"range":"E2:E7","rule":{"type":"dataBar","color":"#5B9BD5"}}' \
  --cmd 'view.freezeTopRow' --out dashboard.xlsx

gridcraft-cli run --in report.xlsx \
  --cmd 'insert.pivotTable={"source":"sales!A1:E7","rows":["Region"],"values":[{"field":"Revenue","func":"sum"}]}' \
  --out pivot.xlsx       # report goes on a new sheet at A3
```

Filter with `data.filter` then `data.filterBy={"column":"A","values":["North"]}`.

## Scripts

For long edits put one command per line in a file (`id {json}`, `id={json}` or
`{"command":...,"params":...}`; `#` comments allowed):

```bash
gridcraft-cli run --in report.xlsx --script steps.jsonl --out book.xlsx --print B1 --sheet Summary
# steps.jsonl:
#   home.insertSheet {"name":"Summary"}
#   cell.set={"cell":"A1","input":"Total revenue","sheet":"Summary"}
#   cell.set={"cell":"B1","input":"=SUM(sales!E2:E7)","sheet":"Summary"}
```

## Export

```bash
gridcraft-cli convert report.xlsx report.csv --sheet sales   # .xlsx .csv .tsv .json .html
gridcraft-cli run --in report.xlsx --cmd 'file.exportPdf={"path":"/abs/path/report.pdf","fitToPage":true}' --quiet
```

Check results with `cat`/`info`, or `sheet.read` in a `run` to get values as JSON.
