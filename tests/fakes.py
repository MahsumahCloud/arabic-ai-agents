"""A fake Anthropic client for offline tests.

It returns scripted responses shaped like the real SDK objects (only the
attributes the course code reads), and records every request it receives.
"""

from __future__ import annotations

import copy
import itertools
from types import SimpleNamespace

_ids = itertools.count(1)


def text(value: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=value)


def thinking(value: str = "") -> SimpleNamespace:
    return SimpleNamespace(type="thinking", thinking=value, signature="sig")


def tool_use(name: str, tool_input: dict, block_id: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=block_id or f"toolu_{next(_ids):04d}", name=name, input=tool_input)


def usage(input_tokens: int = 100, output_tokens: int = 50, cache_write: int | None = None, cache_read: int | None = None):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_write,
        cache_read_input_tokens=cache_read,
    )


def response(*blocks, stop_reason: str = "end_turn", tokens=None) -> SimpleNamespace:
    return SimpleNamespace(content=list(blocks), stop_reason=stop_reason, usage=tokens or usage())


class _Messages:
    def __init__(self, scripted):
        self._scripted = list(scripted)
        self.requests: list[dict] = []

    def create(self, **kwargs):
        # Snapshot the request: the caller keeps mutating its messages list.
        self.requests.append(copy.deepcopy(kwargs))
        if not self._scripted:
            raise AssertionError("FakeClient ran out of scripted responses")
        item = self._scripted.pop(0)
        return item(kwargs) if callable(item) else item


class FakeClient:
    def __init__(self, scripted):
        self.messages = _Messages(scripted)

    @property
    def requests(self) -> list[dict]:
        return self.messages.requests
