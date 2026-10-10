#!/usr/bin/env python3
"""Regenerate every manifest, marketplace entry and installer from PLUGINS below.

Run from anywhere: python3 tools/generate.py
Edit this file (or tools/install-runtime.template), not the generated files.
"""
import json
import os
import stat
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = "creative-plugins"
OWNER = {"name": "Prajvis"}
REPOSITORY = "https://github.com/prajvis/creative-plugins"
LICENSE = "Apache-2.0"
MARKETPLACE_DESCRIPTION = (
    "Agent plugins for the open-source Crafting Apps (images, video, photos, vectors, PDFs, "
    "motion graphics, page layout, spreadsheets and CAD), driven headlessly through their "
    "official CLIs"
)
AUTHOR = {"name": "Prajvis"}

PLUGINS = [
    {
        "name": "photocraft",
        "display": "PhotoCraft",
        "version": "0.1.1",
        "description": "Edit images headlessly with PhotoCraft, an open-source Photoshop-style editor: "
        "crop, adjustments, filters, layers, masks, compositing and PSD export. "
        "Installs the official photocraft-cli into the plugin's bin/.",
        "keywords": ["photocraft", "image-editing", "photoshop", "psd", "cli"],
        "category": "Design",
    },
    {
        "name": "filmcraft",
        "display": "FilmCraft",
        "version": "0.1.1",
        "description": "Edit video headlessly with FilmCraft, an open-source Premiere-style editor: "
        "import media, build sequences, cut, apply effects, render frames and export. "
        "Installs the official filmcraft-cli into the plugin's bin/.",
        "keywords": ["filmcraft", "video-editing", "premiere", "cli"],
        "category": "Design",
    },
    {
        "name": "lightcraft",
        "display": "LightCraft",
        "version": "0.1.1",
        "description": "Develop and export photos headlessly with LightCraft, an open-source "
        "Lightroom-style raw developer: exposure, colour, presets, auto settings, HDR/panorama "
        "merge and batch export. Installs the official lightcraft-cli into the plugin's bin/.",
        "keywords": ["lightcraft", "photo-editing", "lightroom", "raw", "cli"],
        "category": "Design",
    },
    {
        "name": "vectorcraft",
        "display": "VectorCraft",
        "version": "0.1.0",
        "description": "Create and edit vector artwork headlessly with VectorCraft, an open-source Illustrator-style editor: shapes, paths, text, gradients, live effects, Pathfinder, artboards, image trace and conversion between SVG, PDF, AI, EPS, DXF and PNG/JPEG. Installs the official vectorcraft-cli into the plugin's bin/.",
        "keywords": ["vectorcraft", "cli", "vector", "svg", "illustration"],
        "category": "Design",
    },
    {
        "name": "pdfcraft",
        "display": "PdfCraft",
        "version": "0.1.0",
        "description": "Work on PDFs headlessly with PdfCraft, an open-source Acrobat-style editor: merge, split, reorder and rotate pages, extract text and images, render pages, fill forms, passwords, redaction, watermarks, OCR and Word/HTML export. Installs the official pdfcraft-cli into the plugin's bin/.",
        "keywords": ["pdfcraft", "pdf", "merge", "forms", "cli"],
        "category": "Productivity",
        "data": {"src": "share/pdfcraft/models", "dest": "models"},
    },
    {
        "name": "effectcraft",
        "display": "EffectCraft",
        "version": "0.1.0",
        "description": "Create motion graphics headlessly with EffectCraft, an open-source After Effects-style compositor: compositions, text, shape, solid and footage layers, keyframes, expressions, effects, masks and scripting, rendered to H.264, ProRes, WebM, GIF, image sequences or Lottie. Installs the official effectcraft-cli into the plugin's bin/.",
        "keywords": ["effectcraft", "cli", "motion-graphics", "animation", "video"],
        "category": "Design",
    },
    {
        "name": "designcraft",
        "display": "DesignCraft",
        "version": "0.1.0",
        "description": "Lay out pages headlessly with DesignCraft, an open-source InDesign-style publishing app: documents and pages, text and graphic frames, threaded stories, styles, parent pages, tables, TOC, data merge, packaging and export to PDF, PNG, IDML and EPUB. Installs the official designcraft-cli into the plugin's bin/.",
        "keywords": ["designcraft", "cli", "layout", "publishing", "pdf"],
        "category": "Design",
    },
    {
        "name": "gridcraft",
        "display": "GridCraft",
        "version": "0.1.0",
        "description": "Build and analyse spreadsheets headlessly with GridCraft, an open-source Excel-style spreadsheet app: cells and formulas, formatting, sort and filter, tables, charts, pivot tables and conversion between XLSX, CSV, TSV, JSON, HTML and PDF. Installs the official gridcraft-cli into the plugin's bin/.",
        "keywords": ["gridcraft", "cli", "spreadsheet", "xlsx", "excel"],
        "category": "Productivity",
    },
    {
        "name": "cadcraft",
        "display": "CADCraft",
        "version": "0.1.0",
        "description": "Draft 2D CAD drawings headlessly with CADCraft, an open-source AutoCAD-style drafting app: lines, polylines, circles, text, layers, dimensions, hatches, blocks, arrays and edits by handle, with DXF/DWG open and save and SVG, PNG and PDF export. Installs the official cadcraft-cli into the plugin's bin/.",
        "keywords": ["cadcraft", "cli", "cad", "dxf", "drafting"],
        "category": "Design",
    },
]


def write(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    mode = 0o755 if executable else 0o644
    os.chmod(path, mode)


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    template = (REPO / "tools" / "install-runtime.template").read_text()
    for p in PLUGINS:
        root = REPO / "plugins" / p["name"]
        common = {
            "name": p["name"],
            "version": p["version"],
            "description": p["description"],
            "author": AUTHOR,
            "homepage": REPOSITORY,
            "repository": REPOSITORY,
            "license": LICENSE,
            "keywords": p["keywords"],
        }
        # Portable Agent Plugins manifest (Codex prefers it; strict schema, no extra keys).
        write(root / "plugin.json", dump({
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **common}))
        # Claude Code: skills/ is discovered by default; bin/ is put on the Bash PATH.
        write(root / ".claude-plugin" / "plugin.json", dump(common))
        # Cursor and the Codex compatibility manifest point at skills/ explicitly.
        write(root / ".cursor-plugin" / "plugin.json", dump({**common, "skills": "./skills/"}))
        write(root / ".codex-plugin" / "plugin.json", dump({**common, "skills": "./skills/"}))
        write(root / "bin" / ".keep", "")
        # The installer sits next to the CLI in bin/, so it's on PATH wherever bin/ is.
        write(root / "bin" / f"{p['name']}-install",
              template.replace("__TOOL__", p["name"])
              .replace("__DATA_SRC__", p.get("data", {}).get("src", ""))
              .replace("__DATA_DEST__", p.get("data", {}).get("dest", "")),
              executable=True)

    write(REPO / ".claude-plugin" / "marketplace.json", dump({
        "name": MARKETPLACE,
        "description": MARKETPLACE_DESCRIPTION,
        "owner": OWNER,
        "plugins": [{
            "name": p["name"],
            "source": f"./plugins/{p['name']}",
            "description": p["description"],
            "version": p["version"],
        } for p in PLUGINS],
    }))
    write(REPO / ".cursor-plugin" / "marketplace.json", dump({
        "name": MARKETPLACE,
        "owner": OWNER,
        "metadata": {"description": MARKETPLACE_DESCRIPTION},
        "plugins": [{
            "name": p["name"],
            "source": f"plugins/{p['name']}",
            "description": p["description"],
            "version": p["version"],
        } for p in PLUGINS],
    }))
    write(REPO / ".agents" / "plugins" / "marketplace.json", dump({
        "name": MARKETPLACE,
        "interface": {"displayName": "Creative Plugins"},
        "plugins": [{
            "name": p["name"],
            "source": {"source": "local", "path": f"./plugins/{p['name']}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": p["category"],
        } for p in PLUGINS],
    }))
    print("generated:", ", ".join(p["name"] for p in PLUGINS))


if __name__ == "__main__":
    main()
