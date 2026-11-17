"""Lesson 05: what an agent skill is, and how an agent decides to load one.

A skill is a folder. Inside it, SKILL.md starts with a short front matter
(name + description) and continues with the instructions:

    my-skill/
      SKILL.md          <- required: front matter, then instructions
      scripts/          <- optional: helpers the instructions may mention
      resources/        <- optional: templates, examples, reference text

The agent does not read every skill in full. It keeps only one line per skill
(name + description) in view, and opens the full SKILL.md only when a request
matches that description. So the description is the trigger: if it doesn't say
when to use the skill, the skill is never used.

This file has no model in it: `pick_skill` imitates that decision with plain
word overlap, so you can see the mechanism and test it offline.

Run:
    python lessons/05/skill_loader.py "حوّل التاريخ الهجري إلى ميلادي"
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MIN_TRIGGER_WORDS = 2  # how many request words must appear in a description


class SkillError(ValueError):
    """A SKILL.md that breaks the rules. Messages are in Arabic for the reader."""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    body: str
    folder: Path | None = None
    meta: tuple[tuple[str, str], ...] = ()


# ---- reading SKILL.md --------------------------------------------------------

def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Return (front matter as a dict, the body after it).

    Only the small subset we need: `key: value` lines between two `---` lines.
    Values may be wrapped in single or double quotes.
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillError("يجب أن يبدأ SKILL.md بسطر --- ثم الاسم والوصف")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise SkillError("لم يُغلق رأس الملف بسطر ---") from None
    meta: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise SkillError(f"السطر {number} في الرأس ليس بالصيغة key: value")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, "\n".join(lines[end + 1 :]).strip()


def parse_skill(text: str, folder: Path | None = None) -> Skill:
    meta, body = split_front_matter(text)
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not name:
        raise SkillError("الحقل name مفقود")
    if len(name) > MAX_NAME or not NAME.match(name):
        raise SkillError("الاسم: حروف إنجليزية صغيرة وأرقام وشرطات فقط، بحد أقصى 64 حرفاً")
    if not description.strip():
        raise SkillError("الحقل description مفقود أو فارغ، ودونه لن يعرف الوكيل متى يستعمل المهارة")
    if len(description) > MAX_DESCRIPTION:
        raise SkillError("الوصف أطول من 1024 حرفاً")
    if not body:
        raise SkillError("لا تعليمات بعد الرأس")
    if folder is not None and folder.name != name:
        raise SkillError(f"اسم المجلد «{folder.name}» لا يطابق name «{name}»")
    rest = tuple((k, v) for k, v in meta.items() if k not in ("name", "description"))
    return Skill(name, description, body, folder, rest)


def read_skill(folder: str | Path) -> Skill:
    folder = Path(folder)
    path = folder / "SKILL.md"
    if not path.is_file():
        raise SkillError(f"لا يوجد SKILL.md في {folder.name}")
    return parse_skill(path.read_text(encoding="utf-8"), folder)


def read_skills(skills_dir: str | Path) -> list[Skill]:
    """Every valid skill folder directly under skills_dir, sorted by name."""
    root = Path(skills_dir)
    if not root.is_dir():
        return []
    return [read_skill(p) for p in sorted(root.iterdir()) if (p / "SKILL.md").is_file()]


# ---- matching words (Arabic-aware, very small) -------------------------------

_TASHKEEL = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_NON_WORD = re.compile(r"[^\w]+")
STOP_WORDS = {
    "في", "من", "الى", "علي", "عن", "مع", "هل", "ما", "لي", "او", "ثم", "هذا", "هذه",
    "كل", "به", "بها", "لا", "ان", "التي", "الذي", "حين", "عند", "the", "a", "an", "to", "of",
}
_PREFIXES = ("وال", "بال", "كال", "فال", "لل", "ال")


def normalize(text: str) -> str:
    text = _TASHKEEL.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").translate(_ARABIC_INDIC)
    return " ".join(_NON_WORD.sub(" ", text).lower().replace("_", " ").split())


def terms(text: str) -> set[str]:
    """Comparable words: normalized, without the article, without stop words."""
    found = set()
    for token in normalize(text).split():
        if token in STOP_WORDS or len(token) < 2:
            continue
        for prefix in _PREFIXES:
            if token.startswith(prefix) and len(token) - len(prefix) >= 3:
                token = token[len(prefix) :]
                break
        found.add(token)
    return found


# ---- what the agent sees, and how it picks ----------------------------------

def index_lines(skills: list[Skill]) -> str:
    """The only text about skills that is always in the agent's view."""
    return "\n".join(f"- {s.name}: {s.description}" for s in skills)


def pick_skill(request: str, skills: list[Skill]) -> Skill | None:
    """The skill whose description shares the most words with the request.

    None when no description shares at least MIN_TRIGGER_WORDS words: better to
    load nothing than the wrong instructions. Ties go to the first by name.
    """
    wanted = terms(request)
    best, best_hits = None, 0
    for skill in skills:
        hits = len(wanted & terms(skill.description))
        if hits > best_hits:
            best, best_hits = skill, hits
    return best if best_hits >= MIN_TRIGGER_WORDS else None


def context_cost(skills: list[Skill]) -> tuple[int, int]:
    """(characters always loaded, characters if every SKILL.md were loaded)."""
    always = len(index_lines(skills))
    everything = always + sum(len(s.body) for s in skills)
    return always, everything


def main(argv: list[str]) -> int:
    here = Path(__file__).parent
    skills = read_skills(here / "catalog" / "skills")
    request = " ".join(argv) or "حوّل التاريخ الهجري إلى ميلادي"
    always, everything = context_cost(skills)
    print(f"skills: {len(skills)} | always in view: {always} chars | if every SKILL.md were loaded: {everything} chars")
    chosen = pick_skill(request, skills)
    if chosen is None:
        print("no skill loaded: no description matches the request")
        return 1
    print(f"loaded: {chosen.name}")
    print(chosen.body.splitlines()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
