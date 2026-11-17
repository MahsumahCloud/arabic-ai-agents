"""Solution 04-2: flag vague words in a spec before an agent guesses their meaning.

"Fast", "simple", "suitable" mean nothing to an agent. Each one should become a
number or a testable rule. This finds them, line by line.
"""

from __future__ import annotations

import re

VAGUE = {
    "سريع", "سريعة", "بسرعة",
    "سهل", "سهلة", "بسهولة",
    "بسيط", "بسيطة",
    "مناسب", "مناسبة",
    "جيد", "جيدة",
    "أفضل", "معقول", "معقولة",
    "تقريباً", "تقريبا",
    "أحياناً", "أحيانا",
    "بعض", "كثير", "كثيرة",
    "إلخ",
}

PREFIXES = ("و", "ف", "ب", "ال", "وال", "بال", "فال")
WORD = re.compile(r"[ء-يـً-ْ]+")
DIACRITICS = re.compile(r"[ـً-ْ]")


def _candidates(word: str) -> set[str]:
    bare = DIACRITICS.sub("", word)
    found = {bare}
    for prefix in PREFIXES:
        if bare.startswith(prefix) and len(bare) - len(prefix) >= 3:
            found.add(bare[len(prefix):])
    return found


def vague_lines(spec_text: str) -> list[tuple[int, str]]:
    """Return (line number, vague word) for every vague word, in order."""
    hits = []
    for number, line in enumerate(spec_text.splitlines(), 1):
        for word in WORD.findall(line):
            match = _candidates(word) & VAGUE
            if match:
                hits.append((number, sorted(match)[0]))
    return hits
