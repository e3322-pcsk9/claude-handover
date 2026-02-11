#!/usr/bin/env bash
# Claude Code dotfiles installer
# Syncs skills, hooks, and merges hook config into settings.local.json
# Safe to run repeatedly — idempotent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.local.json"

echo "Installing Claude Code dotfiles..."

# 1. Symlink skills (entire directory tree)
echo "  Linking skills..."
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    skill_name="$(basename "$skill_dir")"
    target="$CLAUDE_DIR/skills/$skill_name"
    if [ -L "$target" ]; then
        rm "$target"
    elif [ -d "$target" ]; then
        rm -rf "$target"
    fi
    mkdir -p "$CLAUDE_DIR/skills"
    ln -s "$skill_dir" "$target"
    echo "    $skill_name -> linked"
done

# 2. Symlink hooks
echo "  Linking hooks..."
mkdir -p "$CLAUDE_DIR/hooks"
for hook_file in "$SCRIPT_DIR"/hooks/*; do
    hook_name="$(basename "$hook_file")"
    target="$CLAUDE_DIR/hooks/$hook_name"
    if [ -L "$target" ]; then
        rm "$target"
    fi
    ln -sf "$hook_file" "$target"
    echo "    $hook_name -> linked"
done

# 3. Merge hooks config into settings.local.json (preserves existing permissions)
echo "  Merging hook config into settings.local.json..."
if [ ! -f "$SETTINGS" ]; then
    echo '{}' > "$SETTINGS"
fi

# Use python3 (available on all macOS) to do a safe JSON merge
python3 - "$SETTINGS" "$SCRIPT_DIR/hooks.json" <<'PYEOF'
import json, sys

settings_path = sys.argv[1]
hooks_path = sys.argv[2]

with open(settings_path) as f:
    settings = json.load(f)

with open(hooks_path) as f:
    hooks_config = json.load(f)

# Merge hooks key — replace entirely (hooks.json is source of truth)
settings["hooks"] = hooks_config["hooks"]

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

PYEOF

echo ""
echo "Done. Restart Claude Code to pick up changes."
echo ""
echo "Installed:"
echo "  Skills:   $CLAUDE_DIR/skills/"
echo "  Hooks:    $CLAUDE_DIR/hooks/"
echo "  Settings: $SETTINGS"
