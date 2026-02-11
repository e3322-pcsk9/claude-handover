# claude-dotfiles

Portable Claude Code configuration — skills, hooks, and settings that sync across devices.

## What's Included

### `/handover` Skill

Manual slash command that generates a `HANDOVER.md` shift-change report summarizing the current session. Captures completed work, decisions, gotchas, and next steps so the next Claude session can pick up without losing context.

### PreCompact Hook

Automatically generates a dated handover document (`HANDOVER-YYYY-MM-DD.md`) when Claude Code auto-compacts. Only triggers on automatic compaction — manual `/compact` is left alone. Uses `claude -p` to summarize the conversation transcript.

## Install

```bash
git clone https://github.com/e3322-pcsk9/claude-dotfiles.git ~/claude-dotfiles
cd ~/claude-dotfiles
./install.sh
```

Restart Claude Code after installing.

The install script:
- Symlinks skills and hooks into `~/.claude/`
- Merges hook config into `~/.claude/settings.local.json` (preserves existing permissions)
- Is idempotent — safe to run repeatedly

## Uninstall

```bash
cd ~/claude-dotfiles
./uninstall.sh
```

## Update

```bash
cd ~/claude-dotfiles
git pull
```

Files are symlinked, so pulling updates takes effect immediately. No need to re-run install unless new skills or hooks are added.

## Structure

```
├── install.sh          # Symlinks + settings merge
├── uninstall.sh        # Clean removal
├── hooks.json          # Hook config (source of truth)
├── hooks/
│   └── pre-compact-handover.py
└── skills/
    └── handover/
        └── SKILL.md
```

## Adding New Skills/Hooks

1. Add skill to `skills/<name>/SKILL.md`
2. Add hook scripts to `hooks/`
3. Update `hooks.json` if the hook needs settings config
4. Re-run `./install.sh` to pick up new symlinks
5. Commit and push — other devices just `git pull && ./install.sh`
