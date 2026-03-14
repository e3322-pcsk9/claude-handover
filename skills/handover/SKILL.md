---
name: handover
description: Generate a timestamped HANDOVER document summarizing the current session. Use when user types /handover or asks to create a handover document.
---

# Handover Document Generator

Review the **full conversation** from start to finish and compress it into a structured handover document. This serves as a session memory for the next Claude session picking up where this one left off. Optimize for the assistant's ability to continue working, not human readability.

## Filename

**Format:** `SUMMARY-HANDOVER-YYYY-MM-DD-HHMMSS.md`

Example: `fix-login-bug-optimize-db-HANDOVER-2026-02-12-143052.md`

The summary prefix should:
- Capture the core topic of this session in one concise phrase (max ~15 words)
- Be written in the same language as the conversation
- Be sanitized for use in a filename: replace spaces with `-`, remove characters invalid in filenames (`/ \ : * ? " < > |`)
- Be truncated to 30 characters if longer

## Analysis

Before writing, analyze the conversation:

1. What did the user originally request? (Exact phrasing)
2. What actions succeeded? What failed and why?
3. Did the user correct or redirect me at any point?
4. What was I actively working on at the end?
5. What tasks remain incomplete or pending?
6. What specific details (IDs, paths, values, names) must survive compression?

## Summary Format

### User Intent
The user's original request and any refinements. Use direct quotes for key requirements.
If the user's goal evolved during the conversation, capture that progression.

### Completed Work
Actions successfully performed. Be specific:
- What was created, modified, or deleted
- Exact identifiers (file paths, record IDs, URLs, names)
- Specific values, configurations, or settings applied

### Errors & Corrections
- Problems encountered and how they were resolved
- Approaches that failed (so they aren't retried)
- User corrections: "don't do X", "actually I meant Y", "that's wrong because..."
Capture corrections verbatim — these represent learned preferences.

### Active Work
What was in progress when the session ended. Include:
- The specific task being performed
- Direct quotes showing exactly where work left off
- Any partial results or intermediate state

### Pending Tasks
Remaining items the user requested that haven't been started.
Distinguish between "explicitly requested" and "implied/assumed."

### Key References
Important details needed to continue:
- Identifiers: IDs, paths, URLs, names, keys
- Values: numbers, dates, configurations, credentials (redacted)
- Context: relevant background information, constraints, preferences
- Citations: sources referenced during the conversation

## Preserve Rules

Always preserve when present:
- Exact identifiers (IDs, paths, URLs, keys, names)
- Error messages verbatim
- User corrections and negative feedback
- Specific values, formulas, or configurations
- Technical constraints or requirements discovered
- The precise state of any in-progress work

## Compression Rules

- Weight recent messages more heavily — the end of the conversation is the active context
- Omit pleasantries, acknowledgments, and filler ("Sure!", "Great question")
- Keep each section under 500 words; condense older content to make room for recent
- If you must cut details, preserve: user corrections > errors > active work > completed work

## Output

- Use the Write tool to create the file in the current working directory.
- After writing, tell the user where the file was saved and give a one-line summary of the session.
