#!/usr/bin/env python3
"""Pre-compact hook that generates a handover document before auto-compaction.

Reads the conversation transcript, pipes it to `claude -p` to generate
a summary, and saves it as HANDOVER-YYYY-MM-DD.md in the project directory.

Only runs on automatic compaction (matcher: "auto" in settings), not manual /compact.
"""

import json
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


def generate_handover(transcript_text: str, cwd: str) -> str:
    """Call claude -p to generate a handover summary from the transcript."""
    prompt = """You are generating a handover document from a Claude Code session transcript.
Review the conversation and write a concise but comprehensive HANDOVER document with these sections:

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

    return result.stdout.strip()


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

        handover_content = generate_handover(transcript_text, cwd)

        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = Path(cwd) / f"HANDOVER-{date_str}.md"

        # Avoid overwriting — append a counter if file exists
        if output_path.exists():
            counter = 2
            while True:
                output_path = Path(cwd) / f"HANDOVER-{date_str}-{counter}.md"
                if not output_path.exists():
                    break
                counter += 1

        output_path.write_text(f"# Handover — {date_str}\n\n{handover_content}\n")

    except Exception:
        # Never block compaction due to handover failure
        pass

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
