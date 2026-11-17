"""Lesson 05, exercise 2: read a skill's scripts before anyone runs them.

audit() opens every file in a skill folder as text and reports lines that
deserve a human look. It never executes, imports or sources anything. A clean
report does not prove a script is safe; it only means none of these signs showed up.
"""

from __future__ import annotations

import re
from pathlib import Path

SIGNS = [
    (re.compile(r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r"), "حذف قسري لمجلدات"),
    (re.compile(r"\b(curl|wget)\b"), "تنزيل من الشبكة"),
    (re.compile(r"\|\s*(sh|bash|zsh|python3?)\b"), "تشغيل ما يصل من أمر آخر مباشرة"),
    (re.compile(r"\b(eval|exec)\s*\("), "تشغيل نص كشيفرة"),
    (re.compile(r"\bbase64\b"), "نص مُرمَّز قد يخفي ما يفعله"),
    (re.compile(r"\bsudo\b"), "طلب صلاحيات المدير"),
    (re.compile(r"\bchmod\s+777\b"), "صلاحيات مفتوحة للجميع"),
    (re.compile(r"(~|\$HOME)/\.ssh|\.env\b|id_rsa"), "قراءة مفاتيح أو أسرار"),
]


def audit(folder: str | Path) -> list[tuple[str, int, str]]:
    folder = Path(folder)
    found = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != "SKILL.md"):
        if path.is_symlink():
            found.append((path.relative_to(folder).as_posix(), 0, "رابط رمزي"))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for pattern, reason in SIGNS:
                if pattern.search(line):
                    found.append((path.relative_to(folder).as_posix(), number, reason))
    return found
