"""Lesson 03: a tiny local document store with Arabic-aware keyword search.

No vector database, no embeddings. Plain files and a normalizer, so you can
read every line of how retrieval works before reaching for bigger tools.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "corpus"

_TASHKEEL = re.compile("[ً-ْٰـ]")  # harakat, dagger alef, tatweel
_NON_WORD = re.compile(r"[^\w\s]")
_ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# Very small stop-word list: common words that would match almost every line.
STOP_WORDS = {
    "في", "من", "الي", "علي", "عن", "ما", "ماذا", "هل", "كيف", "لماذا", "متي",
    "هو", "هي", "او", "ثم", "مع", "هذا", "هذه", "ذلك", "التي", "الذي", "كان",
    "لا", "لم", "ان", "قد", "كل", "بين", "اين", "كم",
}


def normalize(text: str) -> str:
    """Make Arabic text comparable: drop diacritics, unify letter variants."""
    text = _TASHKEEL.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه")
    text = text.translate(_ARABIC_INDIC)
    text = _NON_WORD.sub(" ", text)
    return " ".join(text.lower().split())


def query_terms(query: str) -> list[str]:
    terms = []
    for token in normalize(query).split():
        if token in STOP_WORDS or len(token) < 2:
            continue
        # Drop the definite article (and a leading waw) so "والنخله" -> "نخله".
        for prefix in ("وال", "بال", "كال", "فال", "ال"):
            if token.startswith(prefix) and len(token) - len(prefix) >= 3:
                token = token[len(prefix):]
                break
        terms.append(token)
    return terms


@dataclass(frozen=True)
class Hit:
    doc_id: str
    line: int
    text: str
    score: int


class Corpus:
    def __init__(self, directory: Path = CORPUS_DIR):
        self.directory = Path(directory)
        self.docs: dict[str, list[str]] = {}
        for path in sorted(self.directory.glob("*.txt")):
            self.docs[path.name] = path.read_text(encoding="utf-8").splitlines()

    def list_documents(self) -> str:
        """One line per document: id, number of lines, and its title (line 1)."""
        rows = [f"{doc_id} ({len(lines)} lines): {lines[0] if lines else ''}" for doc_id, lines in self.docs.items()]
        return "\n".join(rows) if rows else "(empty corpus)"

    def search(self, query: str, limit: int = 8) -> list[Hit]:
        terms = query_terms(query)
        if not terms:
            return []
        hits = []
        for doc_id, lines in self.docs.items():
            for number, line in enumerate(lines, start=1):
                normalized = normalize(line)
                score = sum(1 for term in terms if term in normalized)
                if score:
                    hits.append(Hit(doc_id, number, line, score))
        hits.sort(key=lambda h: (-h.score, h.doc_id, h.line))
        return hits[:limit]

    def read(self, doc_id: str, start: int = 1, end: int | None = None) -> list[tuple[int, str]]:
        if doc_id not in self.docs:
            raise ValueError(f"unknown document: {doc_id}")
        lines = self.docs[doc_id]
        end = len(lines) if end is None else min(end, len(lines))
        if start < 1 or start > end:
            raise ValueError(f"invalid line range {start}-{end} (document has {len(lines)} lines)")
        return [(n, lines[n - 1]) for n in range(start, end + 1)]

    def has_line(self, doc_id: str, line: int) -> bool:
        return doc_id in self.docs and 1 <= line <= len(self.docs[doc_id])
