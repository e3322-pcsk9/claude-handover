---
name: handover
description: Generate a timestamped HANDOVER document summarizing the current session. Use when user types /handover or asks to create a handover document.
---

# Handover Document Generator

Review the **full conversation** from start to finish and write a comprehensive handover document with a descriptive timestamped filename in the current working directory. This document serves as a shift-change report for the next Claude session picking up where this one left off.

**Filename Format:** `一句话总结内容-HANDOVER-YYYY-MM-DD-HHMMSS.md`

Example: `修复登录bug并优化数据库查询-HANDOVER-2026-02-12-143052.md`

The one-sentence summary prefix should:
- Capture the core topic of this session in one concise phrase (max ~15 words)
- Be written in the same language as the conversation
- Be sanitized for use in a filename: replace spaces with `-`, remove characters invalid in filenames (`/ \ : * ? " < > |`)
- Be truncated to 30 characters if longer

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
- **Generate filename:** First compose a one-sentence summary of the session, sanitize it for a filename, then combine with the current timestamp in format `SUMMARY-HANDOVER-YYYY-MM-DD-HHMMSS.md`.
- Use the Write tool to create the file in the current working directory.
- After writing, tell the user where the file was saved and give a brief summary of what's in it.
