#!/usr/bin/env bash
# Static checks for the repo. Optional: --install also downloads and installs each CLI
# into a scratch copy of its plugin and runs it (needs network, ~150 MB download).
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo"
fail=0
err() { echo "FAIL: $*" >&2; fail=1; }

# Generated files must be up to date.
snapshot() {
  find plugins .claude-plugin .cursor-plugin .agents -type f -not -path '*/bin/*-cli' -print0 \
    | sort -z | xargs -0 sha256sum
  find plugins -path '*/bin/*-install' -exec stat -c '%a %n' {} +
}
before="$(snapshot)"
python3 tools/generate.py >/dev/null
after="$(snapshot)"
[[ "$before" == "$after" ]] || err "tools/generate.py changed files; commit its output"

# The repo root must not itself look like a plugin (Prajvis would stop scanning there).
for f in plugin.json .claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json; do
  [[ ! -e "$f" ]] || err "repo root must not contain $f"
done

for json in $(git ls-files '*.json' 2>/dev/null || find . -name '*.json' -not -path './.git/*'); do
  python3 -m json.tool "$json" >/dev/null || err "invalid JSON: $json"
done

for dir in plugins/*/; do
  name="$(basename "$dir")"
  for m in plugin.json .claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json; do
    got="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$dir$m")"
    [[ "$got" == "$name" ]] || err "$dir$m name is '$got', expected '$name'"
  done
  [[ -f "$dir/bin/.keep" ]] || err "$dir/bin/.keep missing"
  [[ -f "$dir/skills/$name/SKILL.md" ]] || err "$dir/skills/$name/SKILL.md missing"
  head -5 "$dir/skills/$name/SKILL.md" | grep -q "^name: $name\$" || err "$name SKILL.md frontmatter name"
  s="$dir/bin/$name-install"
  [[ -x "$s" ]] || err "$s is not executable"
  bash -n "$s" || err "$s has a syntax error"
  # Prajvis rewrites these tokens inside plugin scripts; the installer must not rely on them.
  if grep -nE '\$\{?(CLAUDE_|CURSOR_)?PLUGIN_ROOT' "$s"; then err "$s uses a plugin-root token"; fi
  if command -v shellcheck >/dev/null 2>&1; then shellcheck "$s" || err "shellcheck $s"; fi
  extra="$(git ls-files "$dir/bin" 2>/dev/null | grep -vE "/bin/(\.keep|$name-install)\$" || true)"
  [[ -z "$extra" ]] || err "binaries must not be committed: $extra"
done

if [[ "${1:-}" == "--install" ]]; then
  scratch="$(mktemp -d)"
  trap 'rm -rf "$scratch"' EXIT
  export XDG_RUNTIME_DIR="$scratch/xdg"; mkdir -p "$XDG_RUNTIME_DIR"; chmod 700 "$XDG_RUNTIME_DIR"
  for dir in plugins/*/; do
    name="$(basename "$dir")"
    cp -R "$dir" "$scratch/$name"
    "$scratch/$name/bin/$name-install" || { err "install $name"; continue; }
    "$scratch/$name/bin/$name-cli" --version || err "$name-cli --version"
    "$scratch/$name/bin/$name-install" --check || err "$name --check after install"
  done
fi

[[ "$fail" -eq 0 ]] && echo "all checks passed"
exit "$fail"
