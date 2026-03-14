#!/usr/bin/env bash
# Claude Code dotfiles installer
# Syncs skills, hooks, and merges hook config into settings.json (user scope)
# Safe to run repeatedly — idempotent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"
SETTINGS_LOCAL="$CLAUDE_DIR/settings.local.json"

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

# 3. Merge hooks config into settings.json (entry-level upsert by command)
echo "  Merging hook config into settings.json..."
if [ ! -f "$SETTINGS" ]; then
    echo '{}' > "$SETTINGS"
fi

# Use python3 (available on all macOS) to do a safe JSON merge
python3 - "$SETTINGS" "$SETTINGS_LOCAL" "$SCRIPT_DIR/hooks.json" <<'PYEOF'
import json, sys, os

settings_path = sys.argv[1]
settings_local_path = sys.argv[2]
hooks_path = sys.argv[3]

with open(settings_path) as f:
    settings = json.load(f)

with open(hooks_path) as f:
    hooks_config = json.load(f)

# Collect all commands we own (from hooks.json)
our_commands = set()
for event_key, event_entries in hooks_config.get("hooks", {}).items():
    for entry in event_entries:
        for hook in entry.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                our_commands.add(cmd)

# Upsert our entries into settings.json by matching on command
if "hooks" not in settings:
    settings["hooks"] = {}

for event_key, new_entries in hooks_config["hooks"].items():
    if event_key not in settings["hooks"]:
        settings["hooks"][event_key] = []

    existing = settings["hooks"][event_key]

    for new_entry in new_entries:
        new_cmds = {h.get("command", "") for h in new_entry.get("hooks", [])}
        # Find and replace existing entry with matching command, or append
        replaced = False
        for i, ex_entry in enumerate(existing):
            ex_cmds = {h.get("command", "") for h in ex_entry.get("hooks", [])}
            if ex_cmds & new_cmds:  # any overlap in commands
                existing[i] = new_entry
                replaced = True
                break
        if not replaced:
            existing.append(new_entry)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

# Migration: remove our entries from settings.local.json to prevent double execution
if os.path.exists(settings_local_path):
    with open(settings_local_path) as f:
        local_settings = json.load(f)

    if "hooks" in local_settings:
        for event_key in list(local_settings["hooks"].keys()):
            entries = local_settings["hooks"][event_key]
            filtered = [
                entry for entry in entries
                if not any(
                    h.get("command", "") in our_commands
                    for h in entry.get("hooks", [])
                )
            ]
            if filtered:
                local_settings["hooks"][event_key] = filtered
            else:
                del local_settings["hooks"][event_key]

        if not local_settings["hooks"]:
            del local_settings["hooks"]

        with open(settings_local_path, "w") as f:
            json.dump(local_settings, f, indent=2)
            f.write("\n")

PYEOF

echo ""
echo "Done. Restart Claude Code to pick up changes."
echo ""
echo "Installed:"
echo "  Skills:   $CLAUDE_DIR/skills/"
echo "  Hooks:    $CLAUDE_DIR/hooks/"
echo "  Settings: $SETTINGS"
