#!/usr/bin/env python3
"""SessionStart hook: inject the roadmap's current position and the session rules into context."""

import os
import re
import sys
from pathlib import Path

project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
roadmap = project_dir / "docs" / "roadmap.md"

position = "(docs/roadmap.md not found)"
if roadmap.exists():
    text = roadmap.read_text(encoding="utf-8")
    match = re.search(r"## 当前位置\n(.*?)(?=\n---|\n## )", text, re.S)
    if match:
        position = match.group(1).strip()

print(
    f"""[项目会话开始]
当前位置（来自 docs/roadmap.md）：
{position}

本次会话规则提醒：
1. 先用一句话告诉 Logan 当前所在里程碑和下一步。
2. 做功能必须走 /feature：先进 plan mode 出方案，Logan 确认后才能写代码。
3. 新依赖或新技术先走 /adr。
4. 结束时运行 /wrap-up。
详细规则见 CLAUDE.md 和 docs/workflow.md。"""
)
sys.exit(0)
