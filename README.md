# Creative Plugins

Agent plugins for open-source creative apps. Each plugin gives an agent the app's official headless
CLI plus a skill that explains how to use it. Works with Claude Code, Cursor, Codex and Prajvis.

| Plugin | App | CLI | Use it for |
|---|---|---|---|
| `photocraft` | [PhotoCraft](https://github.com/storytold/photocraft) | `photocraft-cli` | Photoshop-style editing: crop, adjustments, filters, layers, masks, compositing, PSD |
| `filmcraft` | [FilmCraft](https://github.com/storytold/filmcraft) | `filmcraft-cli` | Premiere-style video editing: import, sequences, cuts, effects, frame renders, export |
| `lightcraft` | [LightCraft](https://github.com/storytold/lightcraft) | `lightcraft-cli` | Lightroom-style photo development: exposure, colour, presets, HDR/panorama, export |

PhotoCraft, FilmCraft and LightCraft are open-source apps made by the ArtCraft Team. These plugins
are unofficial and are not made, sponsored or endorsed by the ArtCraft Team. Photoshop, Premiere and
Lightroom are trademarks of Adobe; they are mentioned only to describe what each app does.

Each plugin is self-contained and installs on its own.

## How the binary gets into `bin/`

The repo does not commit binaries. Each plugin ships:

```text
plugins/<name>/
├── plugin.json                 # portable Agent Plugins manifest (Codex)
├── .claude-plugin/plugin.json  # Claude Code
├── .cursor-plugin/plugin.json  # Cursor (also what Prajvis reads)
├── .codex-plugin/plugin.json   # Codex compatibility manifest
├── bin/.keep                   # keeps bin/ in git; the CLI is installed here
├── bin/<name>-install          # downloader, next to the CLI so it's on PATH too
└── skills/<name>/SKILL.md      # how to use it
```

The agent (or you) runs `<name>-install` once. It:

1. resolves the latest GitHub release (or `--version vX.Y.Z`) without using the GitHub API,
2. picks the asset for this machine (Linux x86_64/aarch64 tarball or the macOS universal CLI zip),
3. verifies it against the release's `SHA256SUMS.txt`,
4. extracts only `<name>-cli`, checks that it runs and reports the expected version,
5. renames it into `bin/<name>-cli` atomically.

All paths are relative to the script (it installs into its own directory), so it works wherever the host puts the plugin. Re-running is a
no-op when the latest version is already installed. `--check` reports installed vs latest (exit 0 up to
date, 1 missing, 3 update available); `--force` reinstalls. Concurrent runs wait on a lock in `bin/`.

Windows isn't supported by the installer; use the upstream portable zip.

## Install

**Claude Code**

```text
/plugin marketplace add prajvis/creative-plugins
/plugin install photocraft@creative-plugins
```

Claude Code puts the plugin's `bin/` on the Bash PATH, so the agent runs `photocraft-install` and
`photocraft-cli` by name.

**Cursor**: add this repository as a plugin source; `.cursor-plugin/marketplace.json` lists the three
plugins. Cursor doesn't document adding plugin `bin/` folders to PATH; add the plugin's `bin/` to PATH
yourself or the commands won't be found by name.

**Codex**: `codex plugin marketplace add https://github.com/prajvis/creative-plugins.git`, then install
from the `creative-plugins` marketplace (`.agents/plugins/marketplace.json`).

**Prajvis**: add the repository as a plugin source and attach the plugins you want. Prajvis puts
`/plugins/*/bin` on PATH. The plugin directory is read-only in the sandbox except for each attached
plugin's `bin/`, which is writable only on the agent owner's superuser computer, and only for
plugins attached before that computer started. So: attach, start a new conversation, then run
`<name>-install` (the skill tells the agent to do this). A plugin refresh
resyncs the plugin from git and removes the downloaded CLI; run the installer again afterwards.

## Maintaining

Manifests, marketplaces and the three installers are generated:

```bash
python3 tools/generate.py          # after editing tools/generate.py or tools/install-runtime.template
bash tools/check.sh                # static checks
bash tools/check.sh --install      # also downloads and runs each CLI in a scratch copy
```

Skills (`plugins/*/skills/*/SKILL.md`) are written by hand. Their examples were run against
photocraft-cli 0.5.0, filmcraft-cli 0.4.0 and lightcraft-cli 0.4.0. Upstream releases often, and
`<name>-install` installs the latest, so re-check the examples when a release changes the CLI.

## Licence

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). The Prajvis name is covered by
[TRADEMARKS.md](TRADEMARKS.md).

This repo contains only the plugin wrappers, installers and skills. The CLIs are downloaded from the
official upstream releases and are licensed by their authors under MIT OR Apache-2.0 (see each
upstream repository).
