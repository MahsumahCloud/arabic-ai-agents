"""Lesson 00: check that your environment is ready.

Run:
    python lessons/00/check_setup.py

This script never prints your API key. It only reports whether the
environment variable exists.
"""

from __future__ import annotations

import importlib.util
import os
import sys

MIN_PYTHON = (3, 10)
KEY_VAR = "ANTHROPIC_API_KEY"


def check_python(version_info=sys.version_info) -> tuple[bool, str]:
    ok = tuple(version_info[:2]) >= MIN_PYTHON
    found = f"{version_info[0]}.{version_info[1]}"
    need = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    return ok, f"Python {found} (need {need}+)"


def check_sdk() -> tuple[bool, str]:
    if importlib.util.find_spec("anthropic") is None:
        return False, "anthropic SDK not installed: pip install -r requirements.txt"
    import anthropic

    return True, f"anthropic SDK {anthropic.__version__}"


def check_api_key(environ=os.environ) -> tuple[bool, str]:
    value = environ.get(KEY_VAR, "")
    if not value.strip():
        return False, f"{KEY_VAR} is not set (see docs/00-setup)"
    # Never print the key itself, not even part of it.
    return True, f"{KEY_VAR} is set"


def main() -> int:
    checks = [check_python(), check_sdk(), check_api_key()]
    for ok, message in checks:
        print(("[ok]   " if ok else "[fail] ") + message)
    all_ok = all(ok for ok, _ in checks)
    print("\nReady." if all_ok else "\nFix the items marked [fail], then run again.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
