#!/usr/bin/env bash
# Remove Claude Code dotfiles (skills, hooks, hook config)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"
SETTINGS_LOCAL="$CLAUDE_DIR/settings.local.json"

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

# 3. Remove only our hook entries from settings.json (and settings.local.json)
python3 - "$SETTINGS" "$SETTINGS_LOCAL" "$SCRIPT_DIR/hooks.json" <<'PYEOF'
import json, sys, os

settings_path = sys.argv[1]
settings_local_path = sys.argv[2]
hooks_path = sys.argv[3]

with open(hooks_path) as f:
    hooks_config = json.load(f)

# Collect all commands we own
our_commands = set()
for event_key, event_entries in hooks_config.get("hooks", {}).items():
    for entry in event_entries:
        for hook in entry.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                our_commands.add(cmd)

def remove_our_entries(path):
    """Remove entries whose hooks[].command matches our commands."""
    if not os.path.exists(path):
        return False
    with open(path) as f:
        settings = json.load(f)
    if "hooks" not in settings:
        return False

    changed = False
    for event_key in list(settings["hooks"].keys()):
        entries = settings["hooks"][event_key]
        filtered = [
            entry for entry in entries
            if not any(
                h.get("command", "") in our_commands
                for h in entry.get("hooks", [])
            )
        ]
        if len(filtered) != len(entries):
            changed = True
            if filtered:
                settings["hooks"][event_key] = filtered
            else:
                del settings["hooks"][event_key]

    if changed:
        if not settings["hooks"]:
            del settings["hooks"]
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
    return changed

if remove_our_entries(settings_path):
    print("  Removed our hook entries from settings.json")
if remove_our_entries(settings_local_path):
    print("  Removed our hook entries from settings.local.json")
PYEOF

echo "Done."
