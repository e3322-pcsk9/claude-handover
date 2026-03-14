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


SESSION_MEMORY_PROMPT = """You are generating a session memory document from a Claude Code session transcript.

First, output a ONE-SENTENCE summary (in the same language as the conversation, max 15 words) of what this session was about, on a single line starting with "SUMMARY:".

Then output the separator line: "---CONTENT---"

Then compress the conversation into a structured summary that preserves all information needed to continue work seamlessly. Optimize for the assistant's ability to continue working, not human readability.

<analysis-instructions>
Before generating your summary, analyze the transcript in <think>...</think> tags:
1. What did the user originally request? (Exact phrasing)
2. What actions succeeded? What failed and why?
3. Did the user correct or redirect the assistant at any point?
4. What was actively being worked on at the end?
5. What tasks remain incomplete or pending?
6. What specific details (IDs, paths, values, names) must survive compression?
</analysis-instructions>

<summary-format>
## User Intent
The user's original request and any refinements. Use direct quotes for key requirements.
If the user's goal evolved during the conversation, capture that progression.

## Completed Work
Actions successfully performed. Be specific:
- What was created, modified, or deleted
- Exact identifiers (file paths, record IDs, URLs, names)
- Specific values, configurations, or settings applied

## Errors & Corrections
- Problems encountered and how they were resolved
- Approaches that failed (so they aren't retried)
- User corrections: "don't do X", "actually I meant Y", "that's wrong because..."
Capture corrections verbatim—these represent learned preferences.

## Active Work
What was in progress when the session ended. Include:
- The specific task being performed
- Direct quotes showing exactly where work left off
- Any partial results or intermediate state

## Pending Tasks
Remaining items the user requested that haven't been started.
Distinguish between "explicitly requested" and "implied/assumed."

## Key References
Important details needed to continue:
- Identifiers: IDs, paths, URLs, names, keys
- Values: numbers, dates, configurations, credentials (redacted)
- Context: relevant background information, constraints, preferences
- Citations: sources referenced during the conversation
</summary-format>

<preserve-rules>
Always preserve when present:
- Exact identifiers (IDs, paths, URLs, keys, names)
- Error messages verbatim
- User corrections and negative feedback
- Specific values, formulas, or configurations
- Technical constraints or requirements discovered
- The precise state of any in-progress work
</preserve-rules>

<compression-rules>
- Weight recent messages more heavily—the end of the transcript is the active context
- Omit pleasantries, acknowledgments, and filler ("Sure!", "Great question")
- Omit system context that will be re-injected separately
- Keep each section under 500 words; condense older content to make room for recent
- If you must cut details, preserve: user corrections > errors > active work > completed work
</compression-rules>

Here is the session transcript:

"""


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


def find_plan_paths(transcript_text: str) -> list[str]:
    """Extract plan file paths from transcript text."""
    pattern = r"~/.claude/plans/[a-zA-Z0-9_-]+\.md"
    matches = re.findall(pattern, transcript_text)
    # Expand ~ and deduplicate while preserving order
    seen = set()
    paths = []
    for match in matches:
        expanded = str(Path(match.replace("~", str(Path.home()))))
        if expanded not in seen:
            seen.add(expanded)
            paths.append(expanded)
    return paths


def read_plan_files(plan_paths: list[str]) -> str:
    """Read plan files and format them for appending to handover content."""
    sections = []
    for path in plan_paths:
        p = Path(path)
        if p.exists():
            content = p.read_text()
            original = "~/.claude/plans/" + p.name
            sections.append(
                f"## Associated Plan\n\n"
                f"Source: `{original}`\n\n"
                f"```markdown\n{content}\n```"
            )
    return "\n\n".join(sections)


def generate_handover(transcript_text: str, cwd: str) -> tuple[str, str]:
    """Call claude -p to generate a one-sentence summary and full handover document.

    Returns:
        (summary, handover_content) tuple
    """
    prompt = SESSION_MEMORY_PROMPT
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

        # Detect and embed associated plan files
        plan_paths = find_plan_paths(transcript_text)
        if plan_paths:
            plan_content = read_plan_files(plan_paths)
            if plan_content:
                handover_content = handover_content + "\n\n" + plan_content

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
