"""Lesson 01: your first call to a language model.

Run (needs ANTHROPIC_API_KEY in your environment):
    python lessons/01/first_call.py "ما الفرق بين النموذج اللغوي والوكيل؟"

One request in, one response out. No tools, no loop. This is NOT an agent
yet; it is the building block every agent is made of.
"""

from __future__ import annotations

import os
import sys

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "low"  # low | medium | high | xhigh | max


def get_model() -> str:
    """The model id can be overridden with the AGENT_MODEL env var."""
    return os.environ.get("AGENT_MODEL", DEFAULT_MODEL)


def get_effort() -> str:
    return os.environ.get("AGENT_EFFORT", DEFAULT_EFFORT)


def make_client():
    """Create the real client. The SDK reads ANTHROPIC_API_KEY from the environment.

    The import is inside the function so that tests can run without the SDK.
    """
    import anthropic

    return anthropic.Anthropic()


def extract_text(response) -> str:
    """A response holds a list of content blocks. Keep only the text blocks."""
    return "".join(block.text for block in response.content if block.type == "text")


def ask(client, question: str, *, system: str | None = None, model: str | None = None) -> str:
    """Send one question and return the model's text answer."""
    request = {
        "model": model or get_model(),
        # max_tokens is a ceiling, not a target. You pay only for tokens produced.
        "max_tokens": 16000,
        "output_config": {"effort": get_effort()},
        "messages": [{"role": "user", "content": question}],
    }
    if system:
        request["system"] = system

    response = client.messages.create(**request)

    # Always check why the model stopped before trusting the content.
    if response.stop_reason == "refusal":
        return "[the model declined this request]"
    if response.stop_reason == "max_tokens":
        return extract_text(response) + "\n[answer cut off: max_tokens reached]"
    return extract_text(response)


SYSTEM_AR = "أنت مساعد تعليمي. أجب بالعربية الفصحى في ثلاث جمل على الأكثر."


def main(argv: list[str]) -> int:
    question = argv[1] if len(argv) > 1 else "ما الفرق بين النموذج اللغوي والوكيل الذكي؟"
    client = make_client()
    print(ask(client, question, system=SYSTEM_AR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
