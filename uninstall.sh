#!/usr/bin/env bash
# Remove Claude Code dotfiles (skills, hooks, hook config)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.local.json"

echo "Uninstalling Claude Code dotfiles..."

# 1. Remove skill symlinks
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    skill_name="$(basename "$skill_dir")"
    target="$CLAUDE_DIR/skills/$skill_name"
    if [ -L "$target" ]; then
        rm "$target"
        echo "  Removed skill: $skill_name"
    fi
done

# 2. Remove hook symlinks
for hook_file in "$SCRIPT_DIR"/hooks/*; do
    hook_name="$(basename "$hook_file")"
    target="$CLAUDE_DIR/hooks/$hook_name"
    if [ -L "$target" ]; then
        rm "$target"
        echo "  Removed hook: $hook_name"
    fi
done

# 3. Remove hooks key from settings.local.json
if [ -f "$SETTINGS" ]; then
    python3 - "$SETTINGS" <<'PYEOF'
import json, sys

settings_path = sys.argv[1]
with open(settings_path) as f:
    settings = json.load(f)

settings.pop("hooks", None)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
PYEOF
    echo "  Removed hooks from settings.local.json"
fi

echo "Done."
