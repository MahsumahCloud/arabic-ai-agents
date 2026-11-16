"""Solution 02-2: an approver that logs every decision and never deletes .md files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AuditApprover:
    ask_human: Callable[[str, dict], bool]
    decisions: list[tuple[str, dict, bool, str]] = field(default_factory=list)

    def __call__(self, tool_name: str, tool_input: dict) -> bool:
        path = str(tool_input.get("path", ""))
        if tool_name == "delete_file" and path.lower().endswith(".md"):
            allowed, why = False, "policy: .md files are protected"
        else:
            allowed, why = bool(self.ask_human(tool_name, tool_input)), "human decision"
        self.decisions.append((tool_name, dict(tool_input), allowed, why))
        return allowed
