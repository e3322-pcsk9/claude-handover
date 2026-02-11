---
name: handover
description: Generate a HANDOVER.md shift-change report summarizing the current session. Use when user types /handover or asks to create a handover document.
---

# Handover Document Generator

Review the **full conversation** from start to finish and write a comprehensive handover document to `HANDOVER.md` in the current working directory. This document serves as a shift-change report for the next Claude session picking up where this one left off.

## What to Capture

**Session Summary** — What was being worked on, what's the current status, and what state is the project in right now.

**Completed Work** — Specific things that got done. Include file paths, function names, commands run — enough detail that the next session can verify the work without re-reading every file.

**What Worked / What Didn't** — Bugs encountered, failed approaches, things that turned out to be red herrings, and how issues were ultimately resolved. This is often the most valuable section — it prevents the next session from repeating mistakes.

**Key Decisions & Rationale** — Decisions made during the session and *why* they were made. Include alternatives that were considered and rejected. The next session shouldn't second-guess decisions without understanding the reasoning.

**Lessons Learned & Gotchas** — Surprising behaviors, undocumented quirks, environment-specific issues, or anything the next session should know to avoid wasting time.

**Next Steps** — Clear, actionable items. What should the next session do first? Are there any blockers? Is anything time-sensitive?

**Key Files** — A map of important files that were created, modified, or referenced during the session, with brief notes on what each one does or why it matters.

## Guidelines

- Write in plain, direct language. No fluff.
- Be specific — file paths, line numbers, error messages, command output are all valuable.
- Focus on what the *next session* needs to know, not a chronological replay of the conversation.
- If the session was exploratory or research-heavy, capture findings and conclusions even if no code was written.
- Use the Write tool to create `HANDOVER.md` in the current working directory.
- After writing, tell the user where the file was saved and give a brief summary of what's in it.
