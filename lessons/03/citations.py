"""Lesson 03: check the agent's citations instead of trusting them.

Citation format the agent is asked to use:  [palm.txt:3]  or  [palm.txt:3-5]

A citation is:
  - valid    if the document and lines exist AND the agent actually saw them
  - invalid  if the document or a line does not exist
  - unseen   if it exists, but the agent never retrieved it in this session
             (it may be guessing)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CITATION = re.compile(r"\[([A-Za-z0-9_\-]+\.txt):(\d+)(?:-(\d+))?\]")


@dataclass(frozen=True)
class Citation:
    doc_id: str
    start: int
    end: int

    def __str__(self) -> str:
        span = f"{self.start}" if self.start == self.end else f"{self.start}-{self.end}"
        return f"[{self.doc_id}:{span}]"


@dataclass
class CitationReport:
    valid: list[Citation] = field(default_factory=list)
    invalid: list[Citation] = field(default_factory=list)
    unseen: list[Citation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.valid) and not self.invalid and not self.unseen

    def summary(self) -> str:
        if not (self.valid or self.invalid or self.unseen):
            return "no citations"
        parts = [f"valid {len(self.valid)}"]
        if self.invalid:
            parts.append("invalid " + " ".join(map(str, self.invalid)))
        if self.unseen:
            parts.append("unseen " + " ".join(map(str, self.unseen)))
        return " | ".join(parts)


def parse_citations(text: str) -> list[Citation]:
    found = []
    for doc_id, start, end in CITATION.findall(text):
        first = int(start)
        last = int(end) if end else first
        if last < first:
            first, last = last, first
        found.append(Citation(doc_id, first, last))
    return found


def check_citations(text: str, corpus, seen: dict[str, set[int]]) -> CitationReport:
    report = CitationReport()
    for citation in parse_citations(text):
        lines = range(citation.start, citation.end + 1)
        if not all(corpus.has_line(citation.doc_id, n) for n in lines):
            report.invalid.append(citation)
        elif not all(n in seen.get(citation.doc_id, set()) for n in lines):
            report.unseen.append(citation)
        else:
            report.valid.append(citation)
    return report
