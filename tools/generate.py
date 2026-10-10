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
    "Agent plugins for open-source creative apps: PhotoCraft, FilmCraft and LightCraft, "
    "driven headlessly through their official CLIs"
)
AUTHOR = {"name": "Prajvis"}

PLUGINS = [
    {
        "name": "photocraft",
        "display": "PhotoCraft",
        "version": "0.1.0",
        "description": "Edit images headlessly with PhotoCraft, an open-source Photoshop-style editor: "
        "crop, adjustments, filters, layers, masks, compositing and PSD export. "
        "Installs the official photocraft-cli into the plugin's bin/.",
        "keywords": ["photocraft", "image-editing", "photoshop", "psd", "cli"],
        "category": "Design",
    },
    {
        "name": "filmcraft",
        "display": "FilmCraft",
        "version": "0.1.0",
        "description": "Edit video headlessly with FilmCraft, an open-source Premiere-style editor: "
        "import media, build sequences, cut, apply effects, render frames and export. "
        "Installs the official filmcraft-cli into the plugin's bin/.",
        "keywords": ["filmcraft", "video-editing", "premiere", "cli"],
        "category": "Design",
    },
    {
        "name": "lightcraft",
        "display": "LightCraft",
        "version": "0.1.0",
        "description": "Develop and export photos headlessly with LightCraft, an open-source "
        "Lightroom-style raw developer: exposure, colour, presets, auto settings, HDR/panorama "
        "merge and batch export. Installs the official lightcraft-cli into the plugin's bin/.",
        "keywords": ["lightcraft", "photo-editing", "lightroom", "raw", "cli"],
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
              template.replace("__TOOL__", p["name"]), executable=True)

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
