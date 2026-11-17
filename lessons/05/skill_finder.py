"""Lesson 05: a skill that finds skills, and installs one only when you say yes.

Three parts, all offline:
  1. search:  rank catalogue entries by word overlap with the request, plus
              trust signals (verified source, install count)
  2. rules:   never recommend a low-trust skill, warn about scripts and about
              descriptions that try to trigger on everything
  3. install: copy one skill folder into your skills directory, after showing
              you what will be copied and getting an explicit yes; refuse any
              path that tries to escape the catalogue or the skills directory

The finder never runs anything it installs. It copies files, nothing more.

Run:
    python lessons/05/skill_finder.py "حوّل تاريخاً هجرياً"
    python lessons/05/skill_finder.py --install hijri-dates --to my-skills
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from skill_loader import NAME, SkillError, normalize, read_skill, terms

HERE = Path(__file__).parent
CATALOG = HERE / "catalog" / "catalog.json"

MIN_INSTALLS = 500        # below this, an unverified skill is low trust
RELEVANCE_WEIGHT = 0.7    # the rest of the score is trust
TOP = 3                   # how many recommendations to show
BROAD_TRIGGERS = ("دائما", "مع اي طلب", "كل طلب", "دون ان تسال")


class InstallError(RuntimeError):
    """Installation refused. Messages are in Arabic for the reader."""


@dataclass(frozen=True)
class Entry:
    name: str
    path: str
    description: str
    tags: tuple[str, ...]
    installs: int
    verified: bool


@dataclass(frozen=True)
class Match:
    entry: Entry
    relevance: float
    trust: float

    @property
    def score(self) -> float:
        return round(RELEVANCE_WEIGHT * self.relevance + (1 - RELEVANCE_WEIGHT) * self.trust, 3)


@dataclass
class SearchResult:
    recommended: list[Match] = field(default_factory=list)
    held_back: list[Match] = field(default_factory=list)  # relevant, but low trust


# ---- the catalogue -------------------------------------------------------------

def load_catalog(path: str | Path = CATALOG) -> list[Entry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = []
    for item in data["skills"]:
        installs = item.get("installs", 0)
        if not isinstance(installs, int) or isinstance(installs, bool) or installs < 0:
            raise ValueError(f"installs must be a whole number >= 0: {item.get('name')}")
        entries.append(Entry(
            name=str(item["name"]),
            path=str(item["path"]),
            description=str(item.get("description", "")),
            tags=tuple(str(t) for t in item.get("tags", [])),
            installs=installs,
            verified=item.get("verified") is True,  # only a real true counts
        ))
    return entries


def find(entries: list[Entry], name: str) -> Entry | None:
    return next((e for e in entries if e.name == name), None)


# ---- trust and relevance ---------------------------------------------------------

def trust(entry: Entry) -> float:
    """0..1. A verified source counts most; installs add up to 0.4 on a log scale."""
    installs = 0.4 * min(1.0, math.log10(entry.installs + 1) / 4)
    return round((0.6 if entry.verified else 0.0) + installs, 3)


def is_low_trust(entry: Entry) -> bool:
    return not entry.verified and entry.installs < MIN_INSTALLS


def relevance(query: str, entry: Entry) -> float:
    """Share of the request's words found in the name, description or tags."""
    wanted = terms(query)
    if not wanted:
        return 0.0
    have = terms(" ".join([entry.name.replace("-", " "), entry.description, *entry.tags]))
    return round(len(wanted & have) / len(wanted), 3)


def search(entries: list[Entry], query: str, top: int = TOP) -> SearchResult:
    matches = [Match(e, relevance(query, e), trust(e)) for e in entries]
    matches = sorted((m for m in matches if m.relevance > 0), key=lambda m: (-m.score, m.entry.name))
    result = SearchResult()
    for match in matches:
        (result.held_back if is_low_trust(match.entry) else result.recommended).append(match)
    result.recommended = result.recommended[:top]
    return result


# ---- what the user sees before saying yes ---------------------------------------

def warnings(skill_folder: Path) -> list[str]:
    found = []
    files = [p for p in skill_folder.rglob("*") if p.is_file()]
    if any(p.name != "SKILL.md" for p in files):
        found.append("فيها ملفات غير SKILL.md (سكربتات أو موارد): اقرأها قبل التثبيت، وأداة البحث لا تشغّلها أبداً")
    text = normalize((skill_folder / "SKILL.md").read_text(encoding="utf-8"))
    for phrase in BROAD_TRIGGERS:
        if phrase in text:
            found.append(f"الوصف أو التعليمات تحاول أن تعمل مع كل شيء («{phrase}»): علامة خطر")
            break
    return found


def preview(entry: Entry, skill_folder: Path) -> str:
    files = sorted(p.relative_to(skill_folder).as_posix() for p in skill_folder.rglob("*") if p.is_file())
    lines = [
        f"المهارة: {entry.name}",
        f"الوصف: {entry.description}",
        f"المصدر موثّق: {'نعم' if entry.verified else 'لا'} | التثبيتات: {entry.installs:,}",
        "الملفات: " + "، ".join(files),
    ]
    lines += [f"تنبيه: {w}" for w in warnings(skill_folder)]
    return "\n".join(lines)


# ---- installing -------------------------------------------------------------------

def _inside(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def install(
    entry: Entry,
    catalog_root: str | Path,
    skills_dir: str | Path,
    confirm: Callable[[str], bool],
) -> Path | None:
    """Copy one skill folder into skills_dir. Returns the new folder, or None if the user said no.

    Every check runs before the user is asked, so a "yes" is never wasted on a
    skill that would be refused anyway. Nothing from the skill is executed.
    """
    if not NAME.match(entry.name) or len(entry.name) > 64:
        raise InstallError(f"اسم غير صالح: {entry.name!r}")
    if is_low_trust(entry):
        raise InstallError(f"«{entry.name}» منخفضة الثقة: مصدر غير موثّق وتثبيتات قليلة. لا نثبّتها")

    root = Path(catalog_root).resolve()
    source = (root / entry.path).resolve()
    if source == root or not _inside(source, root):
        raise InstallError(f"المسار «{entry.path}» يخرج من مجلد الفهرس")
    if not source.is_dir():
        raise InstallError(f"لا يوجد مجلد للمهارة: {entry.path}")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise InstallError("في المهارة رابط رمزي (symlink): قد يشير إلى ملف خارجها، فلا نثبّتها")
    try:
        skill = read_skill(source)
    except SkillError as error:
        raise InstallError(f"SKILL.md غير صالح: {error}") from None
    if skill.name != entry.name:
        raise InstallError(f"الفهرس يقول «{entry.name}» والملف يقول «{skill.name}»")

    dest_root = Path(skills_dir).resolve()
    target = dest_root / entry.name
    if target.parent != dest_root:
        raise InstallError("الوجهة تخرج من مجلد المهارات")
    if target.exists():
        raise InstallError(f"«{entry.name}» مثبّتة مسبقاً في {dest_root.name}")

    if confirm(preview(entry, source)) is not True:
        return None
    dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


# ---- command line -----------------------------------------------------------------

def format_result(query: str, result: SearchResult) -> str:
    lines = [f"query: {query}"]
    if not result.recommended:
        lines.append("no trusted skill matches this request")
    for n, m in enumerate(result.recommended, 1):
        source = "verified" if m.entry.verified else "unverified"
        lines.append(f"{n}. {m.entry.name} | score {m.score} | {source}, {m.entry.installs:,} installs")
        lines.append(f"   {m.entry.description}")
    if result.held_back:
        names = ", ".join(m.entry.name for m in result.held_back)
        lines.append(f"held back (low trust, never recommended): {names}")
    return "\n".join(lines)


def ask_human(text: str) -> bool:
    print(text)
    return input("ثبّت؟ اكتب «نعم» للموافقة: ").strip().lower() in {"نعم", "y", "yes"}


def main(argv: list[str]) -> int:
    entries = load_catalog()
    if argv[:1] == ["--install"]:
        if len(argv) != 4 or argv[2] != "--to":
            print("usage: skill_finder.py --install NAME --to DIR", file=sys.stderr)
            return 2
        entry = find(entries, argv[1])
        if entry is None:
            print(f"لا توجد مهارة بهذا الاسم: {argv[1]}", file=sys.stderr)
            return 1
        try:
            target = install(entry, CATALOG.parent, argv[3], ask_human)
        except InstallError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"installed: {target}" if target else "cancelled: nothing was copied")
        return 0
    query = " ".join(argv) or "حوّل تاريخاً هجرياً إلى ميلادي"
    print(format_result(query, search(entries, query)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
