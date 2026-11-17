"""Lesson 04: read the spec and the task list before you let an agent build.

A cheap, offline check of a feature folder (spec.md + tasks.md):
  - every requirement in spec.md (- م-1: ...) is covered by at least one task
  - every task points only at requirements that exist
  - no open question is left in the spec ([يحتاج توضيحاً])
  - which tasks are still unchecked

It does not judge whether a requirement is *good*; that is your job as the
reader. It only catches the gaps that are easy to miss by eye.

Run:
    python lessons/04/spec_check.py lessons/04/example
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

OPEN_QUESTION = "[يحتاج توضيحاً]"

# "- م-1: ..." or "- **م-1**: ..." at the start of a line in spec.md
REQUIREMENT = re.compile(r"^\s*-\s*\**(م-\d+)\**\s*:", re.MULTILINE)
# "- [x] ت-1 (م-1، م-2): ..." in tasks.md
TASK = re.compile(r"^\s*-\s*\[([ xX])\]\s*(ت-\d+)\s*(?:\(([^)]*)\))?\s*:?\s*(.*)$", re.MULTILINE)
REF = re.compile(r"م-\d+")


@dataclass(frozen=True)
class Task:
    task_id: str
    done: bool
    refs: tuple[str, ...]
    text: str


@dataclass
class Report:
    requirements: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)  # requirements with no task
    unknown_refs: list[tuple[str, str]] = field(default_factory=list)  # (task, missing requirement)
    orphan_tasks: list[str] = field(default_factory=list)  # tasks that serve no requirement
    open_questions: list[tuple[int, str]] = field(default_factory=list)  # (line number, line)
    unchecked: list[str] = field(default_factory=list)

    @property
    def ready_to_build(self) -> bool:
        """Safe to hand to the agent: nothing missing, nothing unknown, nothing open."""
        return bool(self.requirements) and not (
            self.uncovered or self.unknown_refs or self.orphan_tasks or self.open_questions
        )

    @property
    def done(self) -> bool:
        return self.ready_to_build and bool(self.tasks) and not self.unchecked


def requirements(spec_text: str) -> list[str]:
    return REQUIREMENT.findall(spec_text)


def tasks(tasks_text: str) -> list[Task]:
    found = []
    for mark, task_id, refs, text in TASK.findall(tasks_text):
        found.append(Task(task_id, mark.lower() == "x", tuple(REF.findall(refs or "")), text.strip()))
    return found


def open_questions(text: str) -> list[tuple[int, str]]:
    return [(n, line.strip()) for n, line in enumerate(text.splitlines(), 1) if OPEN_QUESTION in line]


def check(spec_text: str, tasks_text: str) -> Report:
    report = Report(requirements=requirements(spec_text), tasks=tasks(tasks_text))
    known = set(report.requirements)
    covered = {ref for task in report.tasks for ref in task.refs}
    report.uncovered = [r for r in report.requirements if r not in covered]
    report.unknown_refs = [(t.task_id, r) for t in report.tasks for r in t.refs if r not in known]
    report.orphan_tasks = [t.task_id for t in report.tasks if not t.refs]
    report.open_questions = open_questions(spec_text)
    report.unchecked = [t.task_id for t in report.tasks if not t.done]
    return report


def check_folder(folder: str | Path) -> Report:
    folder = Path(folder)
    return check(
        (folder / "spec.md").read_text(encoding="utf-8"),
        (folder / "tasks.md").read_text(encoding="utf-8"),
    )


# ---- is this idea worth building? -------------------------------------------

ASSESS_QUESTIONS = {
    "real_problem": "هل المشكلة حقيقية، ولها شاهد لا انطباع؟",
    "clear_user": "هل نعرف من سيستعمل الميزة بالتحديد؟",
    "worth_cost": "هل الفائدة المتوقعة أكبر من كلفة البناء والصيانة؟",
    "can_measure": "هل نعرف كيف نقيس نجاحها بعد التشغيل؟",
}


def assess(answers: dict[str, bool | None]) -> str:
    """Return 'go', 'clarify' or 'stop'.

    True = yes with evidence, False = clearly no, None (or missing) = we don't know yet.
    A clear 'no' stops the idea; any unknown sends it back for clarification.
    """
    values = [answers.get(key) for key in ASSESS_QUESTIONS]
    if any(value is False for value in values):
        return "stop"
    if any(value is None for value in values):
        return "clarify"
    return "go"


def format_report(report: Report) -> str:
    lines = [f"requirements: {len(report.requirements)} | tasks: {len(report.tasks)}"]
    for req in report.uncovered:
        lines.append(f"uncovered: {req} has no task")
    for task_id, req in report.unknown_refs:
        lines.append(f"unknown: {task_id} points at {req}, which is not in the spec")
    for task_id in report.orphan_tasks:
        lines.append(f"orphan: {task_id} serves no requirement")
    for number, line in report.open_questions:
        lines.append(f"open question (spec.md:{number}): {line}")
    if report.unchecked:
        lines.append("unchecked: " + ", ".join(report.unchecked))
    lines.append(f"ready to build: {'yes' if report.ready_to_build else 'no'} | done: {'yes' if report.done else 'no'}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    folder = argv[0] if argv else str(Path(__file__).parent / "example")
    report = check_folder(folder)
    print(format_report(report))
    return 0 if report.ready_to_build else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
