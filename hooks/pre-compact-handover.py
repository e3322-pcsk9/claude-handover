#!/usr/bin/env python3
"""Pre-compact hook that generates a handover document before auto-compaction.

Reads the conversation transcript, pipes it to `claude -p` to generate
a summary, and saves it as 一句话总结-HANDOVER-YYYY-MM-DD-HHMMSS.md in the project directory.

Only runs on automatic compaction (matcher: "auto" in settings), not manual /compact.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def read_transcript(transcript_path: str) -> str:
    """Read JSONL transcript and extract human/assistant messages into readable text."""
    messages = []
    with open(transcript_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role", "")
            if role not in ("human", "assistant"):
                continue

            content = entry.get("message", {}).get("content", "")
            if isinstance(content, list):
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = "\n".join(text_parts)

            if content:
                label = "Human" if role == "human" else "Assistant"
                messages.append(f"### {label}\n{content}")

    return "\n\n---\n\n".join(messages)


def sanitize_for_filename(text: str, max_len: int = 20) -> str:
    """Sanitize a string for use as a filename component."""
    # Remove characters invalid in filenames
    text = re.sub(r'[/\\:*?"<>|]', "", text)
    # Replace whitespace with hyphens
    text = re.sub(r"\s+", "-", text.strip())
    # Collapse multiple hyphens
    text = re.sub(r"-{2,}", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    # Truncate to max length
    return text[:max_len]


def generate_handover(transcript_text: str, cwd: str) -> tuple[str, str]:
    """Call claude -p to generate a one-sentence summary and full handover document.

    Returns:
        (summary, handover_content) tuple
    """
    prompt = """You are generating a handover document from a Claude Code session transcript.

First, output a ONE-SENTENCE summary (in the same language as the conversation, max 15 words) of what this session was about, on a single line starting with "SUMMARY:".

Then output the separator line: "---CONTENT---"

Then write the full HANDOVER document with these sections:

## Session Summary
What was being worked on, current status.

## Completed Work
What got done, with specifics (file paths, functions, etc).

## What Worked / What Didn't
Bugs encountered, failed approaches, how issues were resolved.

## Key Decisions & Rationale
Decisions made and why. Alternatives considered.

## Lessons Learned & Gotchas
Surprising behaviors, quirks, things the next session should know.

## Next Steps
Clear actionable items for the next session.

## Key Files
Important files created/modified/referenced with brief notes.

Be specific and direct. Focus on what the next session needs to know.

Here is the session transcript:

"""
    result = subprocess.run(
        ["claude", "-p", prompt + transcript_text],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd,
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed: {result.stderr}")

    output = result.stdout.strip()

    # Parse summary and content
    summary = ""
    handover_content = output

    if "---CONTENT---" in output:
        parts = output.split("---CONTENT---", 1)
        header = parts[0].strip()
        handover_content = parts[1].strip()

        for line in header.splitlines():
            if line.startswith("SUMMARY:"):
                summary = line[len("SUMMARY:"):].strip()
                break

    return summary, handover_content


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        # Can't parse input — let compaction continue
        print(json.dumps({"continue": True}))
        return

    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", ".")

    if not transcript_path or not Path(transcript_path).exists():
        print(json.dumps({"continue": True}))
        return

    try:
        transcript_text = read_transcript(transcript_path)
        if not transcript_text:
            print(json.dumps({"continue": True}))
            return

        summary, handover_content = generate_handover(transcript_text, cwd)

        datetime_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        summary_slug = sanitize_for_filename(summary) if summary else "session"
        output_path = Path(cwd) / f"{summary_slug}-HANDOVER-{datetime_str}.md"

        output_path.write_text(
            f"# Handover — {summary or 'Session'}\n\n{handover_content}\n"
        )

    except Exception:
        # Never block compaction due to handover failure
        pass

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
