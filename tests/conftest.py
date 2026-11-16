from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))


def load(relative_path: str):
    """Import a course file by path (lesson folders start with digits, so they are not packages)."""
    path = ROOT / relative_path
    sys.path.insert(0, str(path.parent))
    name = "course_" + relative_path.replace("/", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses need the module registered
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _no_real_api(monkeypatch):
    """Tests must never reach the network: make sure no key is visible."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("AGENT_MODEL", raising=False)
    monkeypatch.delenv("AGENT_EFFORT", raising=False)
