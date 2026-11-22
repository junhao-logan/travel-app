#!/usr/bin/env python3
"""PostToolUse hook: auto-format the file Claude just edited. Never blocks."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

file_path = payload.get("tool_input", {}).get("file_path", "")
if not file_path or not os.path.exists(file_path):
    sys.exit(0)

path = Path(file_path)
project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, capture_output=True, check=False)


if path.suffix == ".py" and shutil.which("ruff"):
    run(["ruff", "check", "--fix", "--quiet", str(path)])
    run(["ruff", "format", "--quiet", str(path)])

elif path.suffix in {".ts", ".tsx", ".js", ".jsx", ".css", ".json"}:
    # Use the frontend's local prettier if it has been installed.
    for parent in path.parents:
        prettier = parent / "node_modules" / ".bin" / "prettier"
        if prettier.exists():
            run([str(prettier), "--write", "--log-level", "silent", str(path)])
            break
        if parent == project_dir:
            break

sys.exit(0)
