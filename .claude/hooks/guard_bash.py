#!/usr/bin/env python3
"""PreToolUse hook for Bash: block commits/pushes on main and access to .env files.

Exit code 2 blocks the tool call and sends stderr back to Claude.
"""

import json
import re
import subprocess
import sys

try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

command = payload.get("tool_input", {}).get("command", "")


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


# 1. Never touch .env files (allow .env.example).
if re.search(r"(^|[\s/'\"])\.env(?![\w.-])", command):
    block("Blocked: commands must not read or modify .env files. Use .env.example instead.")

# 2. No commits/pushes/merges while on main or master.
if re.search(r"\bgit\s+(commit|push|merge)\b", command):
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    except OSError:
        branch = ""
    if branch in {"main", "master"}:
        block(
            f"Blocked: you are on '{branch}'. Create a feature branch first "
            "(feat/<milestone>-<name>). Direct commits to main are not allowed."
        )

sys.exit(0)
