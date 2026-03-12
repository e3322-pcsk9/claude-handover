# claude-dotfiles

Portable Claude Code configuration — skills, hooks, and settings that sync across devices.

## What's Included

### `/handover` Skill

Manual slash command that generates a timestamped handover document summarizing the current session. Captures completed work, decisions, gotchas, and next steps so the next Claude session can pick up without losing context.

Filename format: `一句话总结内容-HANDOVER-YYYY-MM-DD-HHMMSS.md` — the one-sentence summary prefix is AI-generated from the session content.

#### Vibe
create /handover command. Here's what it does:

How it works: Type /handover at any point during a session, and Claude will look back through everything you two did together and generate a HANDOVER. md file in your current project folder. Think of it like a shift-change report it tells the next Claude exactly where things stand so nothing gets lost between sessions.

What the handover doc covers:

- What you were working on and what got done

- What worked and what didn't including bugs and how they were fixed)

- Key decisions made and why

- Lessons learned and gotchas

- Clear next steps

- A map of important files

### PreCompact Hook

Automatically generates a handover document (`一句话总结内容-HANDOVER-YYYY-MM-DD-HHMMSS.md`) when Claude Code auto-compacts. Only triggers on automatic compaction — manual `/compact` is left alone. Uses `claude -p` to summarize the conversation transcript.

#### Vibe
add more functions:
When Claude Code is about to auto-compact compress the conversation because it's running out of memory), the PreCompact hook fires and:

1. Reads the full conversation transcript while it's still intact

2. Sends it to a fresh Claude instance (claude -p) with instructions to generate a handover summary

3. Saves it as `一句话总结内容-HANDOVER-YYYY-MM-DD-HHMMSS.md` in my project folder

The matcher auto means this only triggers on automatic compaction not when you manually run /compact. This way you're not generating handover docs when you intentionally compact.

must still have /handover too the manual skill still works if you want to generate a handover at any point, not just before compaction.

Files created/modified:

- .claude/hooks/pre-compact-handover.py the script that generates the handover

- .claude/settings.local.json - added the PreCompact hook config


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
