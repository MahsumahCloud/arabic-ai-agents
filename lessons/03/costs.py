"""Lesson 03: track what each agent run costs.

Prices are US dollars per million tokens (MTok), as published for the Claude
API in November 2026. Prices change: check the official pricing page before
relying on these numbers. Unknown models are tracked in tokens only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRICES_PER_MTOK: dict[str, dict[str, float]] = {
    # cache_write is the 5-minute cache write price (about 1.25x input).
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.10},
}


def _count(usage, name: str) -> int:
    """Usage fields can be missing or None (for example when caching is unused)."""
    return int(getattr(usage, name, 0) or 0)


@dataclass
class CostTracker:
    model: str
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0  # includes thinking tokens: they are billed as output
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    per_call_usd: list[float] = field(default_factory=list)

    @property
    def prices(self) -> dict[str, float] | None:
        return PRICES_PER_MTOK.get(self.model)

    def add(self, usage) -> float:
        """Record one response's usage. Returns that call's cost (0.0 if unpriced)."""
        tokens = {
            "input": _count(usage, "input_tokens"),
            "output": _count(usage, "output_tokens"),
            "cache_write": _count(usage, "cache_creation_input_tokens"),
            "cache_read": _count(usage, "cache_read_input_tokens"),
        }
        self.calls += 1
        self.input_tokens += tokens["input"]
        self.output_tokens += tokens["output"]
        self.cache_write_tokens += tokens["cache_write"]
        self.cache_read_tokens += tokens["cache_read"]
        cost = 0.0
        if self.prices:
            cost = sum(tokens[kind] * self.prices[kind] for kind in tokens) / 1_000_000
        self.per_call_usd.append(cost)
        return cost

    @property
    def total_usd(self) -> float:
        return sum(self.per_call_usd)

    def summary(self) -> str:
        price_note = f"${self.total_usd:.4f}" if self.prices else "unpriced model"
        return (
            f"{self.calls} calls | in {self.input_tokens} | out {self.output_tokens} | "
            f"cache w/r {self.cache_write_tokens}/{self.cache_read_tokens} | {price_note}"
        )
