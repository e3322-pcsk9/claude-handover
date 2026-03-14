# claude-handover

Portable Claude Code configuration — skills and hooks that sync across devices via symlinks.

## What's Included

### `/handover` Skill

Manual slash command that generates a timestamped session memory document at any point during a session. Type `/handover` and Claude will review the conversation and write a structured handover file to your current project folder.

Filename format: `{summary-slug}-HANDOVER-YYYY-MM-DD-HHMMSS.md`

### PreCompact Hook

Automatically generates a session memory document when Claude Code auto-compacts. Only fires on automatic compaction — manual `/compact` is unaffected.

**How it works:**
1. Reads the full conversation transcript before compaction
2. Sends it to a fresh Claude instance (`claude -p`) with instructions to compress it into a structured session memory
3. Saves the result as `{summary-slug}-HANDOVER-YYYY-MM-DD-HHMMSS.md` in the project folder

**Session memory format** — optimized for the assistant's ability to continue working, not human readability:
- **User Intent** — original request and refinements, with direct quotes
- **Completed Work** — specific actions, file paths, identifiers, values applied
- **Errors & Corrections** — failed approaches, user corrections verbatim
- **Active Work** — what was in progress when the session ended
- **Pending Tasks** — remaining requested items not yet started
- **Key References** — IDs, paths, URLs, constraints, preferences

## Install

```bash
git clone https://github.com/e3322-pcsk9/claude-handover.git ~/claude-handover
cd ~/claude-handover
./install.sh
```

Restart Claude Code after installing.

The install script:
- Symlinks skills and hooks into `~/.claude/`
- Merges hook config into `~/.claude/settings.local.json` (preserves existing settings)
- Is idempotent — safe to run repeatedly

## Uninstall

```bash
cd ~/claude-handover
./uninstall.sh
```

## Update

```bash
cd ~/claude-handover
git pull
```

Files are symlinked, so pulling updates takes effect immediately. Re-run `./install.sh` only if new skills or hooks were added.

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
2. Add hook script to `hooks/`
3. Update `hooks.json` if the hook needs settings config
4. Re-run `./install.sh` to pick up new symlinks
5. Commit and push — other devices just `git pull && ./install.sh`
