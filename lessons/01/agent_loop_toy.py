"""Lesson 01: the perceive -> think -> act loop, with no AI at all.

Run (no API key needed):
    python lessons/01/agent_loop_toy.py

A hidden number lives in the "environment". The agent cannot see it. It can
only act (make a guess) and perceive (read the feedback "higher", "lower" or
"correct"). Its "brain" here is plain code (binary search). In later lessons
we swap this brain for a language model, but the loop keeps the same shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class NumberEnvironment:
    """The world the agent lives in. It holds a secret and answers guesses."""

    def __init__(self, secret: int, low: int = 1, high: int = 100):
        if not low <= secret <= high:
            raise ValueError("secret must be inside [low, high]")
        self.secret = secret
        self.low = low
        self.high = high

    def respond(self, guess: int) -> str:
        if guess < self.secret:
            return "higher"
        if guess > self.secret:
            return "lower"
        return "correct"


@dataclass
class GuessingAgent:
    low: int
    high: int
    history: list[tuple[int, str]] = field(default_factory=list)  # memory

    def think(self) -> int:
        """Decide the next action from what we know so far."""
        return (self.low + self.high) // 2

    def perceive(self, guess: int, feedback: str) -> None:
        """Update internal state from the environment's feedback."""
        self.history.append((guess, feedback))
        if feedback == "higher":
            self.low = guess + 1
        elif feedback == "lower":
            self.high = guess - 1


def run(env: NumberEnvironment, max_steps: int = 10) -> tuple[bool, list[tuple[int, str]]]:
    """The agent loop. Returns (solved, history).

    Two stopping conditions, as in every real agent:
      1. the goal is reached ("correct"), or
      2. a hard step limit is hit (the guard against endless loops).
    """
    agent = GuessingAgent(low=env.low, high=env.high)
    for _ in range(max_steps):
        guess = agent.think()            # think
        feedback = env.respond(guess)    # act, and the world reacts
        agent.perceive(guess, feedback)  # perceive
        if feedback == "correct":
            return True, agent.history
        if agent.low > agent.high:       # impossible state: stop safely
            break
    return False, agent.history


def main() -> int:
    solved, history = run(NumberEnvironment(secret=73))
    for step, (guess, feedback) in enumerate(history, start=1):
        print(f"step {step}: guess={guess:>3} -> {feedback}")
    print("solved" if solved else "gave up (step limit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
