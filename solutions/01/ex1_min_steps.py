"""Solution 01-1: the smallest step limit that always finds the number.

Binary search halves the range each step, so a range of n numbers needs
ceil(log2(n + 1)) steps in the worst case. For 1..1000 that is 10.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lessons" / "01"))
from agent_loop_toy import NumberEnvironment, run  # noqa: E402


def theoretical_min_steps(low: int, high: int) -> int:
    return math.ceil(math.log2(high - low + 2))


def measured_min_steps(low: int, high: int) -> int:
    """Try every secret and return the worst-case number of steps used."""
    worst = 0
    for secret in range(low, high + 1):
        solved, history = run(NumberEnvironment(secret, low, high), max_steps=64)
        assert solved
        worst = max(worst, len(history))
    return worst


if __name__ == "__main__":
    print("theory:", theoretical_min_steps(1, 1000), "measured:", measured_min_steps(1, 1000))
