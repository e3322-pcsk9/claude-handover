# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Portable Claude Code configuration — skills and hooks that install into `~/.claude/` via symlinks. Changes to source files take effect immediately in the global install without re-running the installer.

## Key Commands

```bash
./install.sh     # Symlink skills/hooks + merge hooks.json into ~/.claude/settings.json
./uninstall.sh   # Remove symlinks + remove our hook entries from settings.json
git pull         # Update (symlinks mean no reinstall needed unless new files added)
```

To test the filename sanitization logic without a live Claude session:
```bash
python3 -c "
import re
def sanitize_for_filename(text, max_len=20):
    text = re.sub(r'[/\\\\:*?\"<>|]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')[:max_len]
print(sanitize_for_filename('your test string'))
"
```

## Architecture

### Install/Uninstall (`install.sh` / `uninstall.sh`)
- Creates symlinks: `skills/<name>/` → `~/.claude/skills/<name>`, `hooks/<file>` → `~/.claude/hooks/<file>`
- Merges `hooks.json` (source of truth for hook config) into `~/.claude/settings.json` using embedded Python
- Merge strategy: entry-level upsert by `hooks[].command` — only touches entries we own, preserves all other hooks
- Migration: also removes any matching entries from `settings.local.json` to prevent double execution
- `uninstall.sh` removes symlinks and removes only our hook entries from both `settings.json` and `settings.local.json`

### Hook (`hooks/pre-compact-handover.py`)
- Triggered by Claude Code's `PreCompact` event (`matcher: "auto"` — only on automatic compaction)
- Reads `transcript_path` from stdin JSON, parses the JSONL conversation, calls `claude -p` to generate a handover summary
- Output format: `{summary_slug}-HANDOVER-YYYY-MM-DD-HHMMSS.md` in the project `cwd`
- The hook never blocks compaction — all errors are swallowed silently (`except Exception: pass`)
- **Cannot be tested via `claude -p` from inside an active Claude Code session** (nested sessions are blocked). Test transcript parsing and filename logic in isolation; full end-to-end only fires on actual auto-compaction.

### Skill (`skills/handover/SKILL.md`)
- Manual `/handover` slash command — prompts Claude to review the session and write a handover doc
- Same filename format as the hook: `{summary_slug}-HANDOVER-YYYY-MM-DD-HHMMSS.md`

### Uninstall (`uninstall.sh`)
- Removes symlinks from `~/.claude/skills/` and `~/.claude/hooks/`
- Removes only our hook entries (matched by command) from `settings.json` and `settings.local.json`

### Hook Config (`hooks.json`)
- Source of truth for which hook entries this repo manages
- `install.sh` upserts entries by matching on `hooks[].command` — other hooks in `settings.json` are preserved

### Generated Handover Files
- Filename format: `{slug}-HANDOVER-YYYY-MM-DD-HHMMSS.md` (slug prefix comes first)
- `.gitignore` pattern `HANDOVER-*.md` does **not** match these — use `*-HANDOVER-*.md` or add `*HANDOVER*.md` to gitignore if you want to exclude them

## Adding New Skills or Hooks

1. Add skill: `skills/<name>/SKILL.md`
2. Add hook script: `hooks/<filename>`
3. If the hook needs settings config, add it to `hooks.json`
4. Re-run `./install.sh` to create new symlinks
5. Commit and push — other devices: `git pull && ./install.sh`
