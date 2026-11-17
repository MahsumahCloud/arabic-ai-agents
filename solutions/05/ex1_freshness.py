"""Lesson 05, exercise 1: an old skill earns less trust.

A skill nobody has updated for a long time may describe tools that changed.
After max_age_days its trust is halved, and it is flagged as stale. A stale
skill that is also unverified is held back like any low-trust skill.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lessons" / "05"))

from skill_finder import Entry, is_low_trust, trust  # noqa: E402

MAX_AGE_DAYS = 365


def is_stale(updated: date, today: date, max_age_days: int = MAX_AGE_DAYS) -> bool:
    if updated > today:
        raise ValueError("تاريخ التحديث في المستقبل: بيانات الفهرس غير صحيحة")
    return (today - updated).days > max_age_days


def fresh_trust(entry: Entry, updated: date, today: date, max_age_days: int = MAX_AGE_DAYS) -> float:
    value = trust(entry)
    return round(value / 2, 3) if is_stale(updated, today, max_age_days) else value


def held_back(entry: Entry, updated: date, today: date, max_age_days: int = MAX_AGE_DAYS) -> bool:
    return is_low_trust(entry) or (not entry.verified and is_stale(updated, today, max_age_days))
