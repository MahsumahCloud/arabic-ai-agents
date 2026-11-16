"""Solution 03-1: keep only the last N questions in the agent's memory.

Two rules make the trimmed history valid:
  1. Cut only at a user message that is a plain question (a string), never
     between a tool_use and its tool_result.
  2. Removing earlier turns changes the conversation that later thinking blocks
     were produced in, so strip ALL thinking blocks from what remains. The model
     loses that earlier reasoning, and the prompt cache restarts. Do this rarely.
"""

from __future__ import annotations

THINKING_TYPES = {"thinking", "redacted_thinking"}


def _block_type(block) -> str | None:
    return block.get("type") if isinstance(block, dict) else getattr(block, "type", None)


def is_question(message: dict) -> bool:
    return message["role"] == "user" and isinstance(message["content"], str)


def trim_history(messages: list[dict], keep_questions: int) -> list[dict]:
    if keep_questions < 1:
        raise ValueError("keep_questions must be at least 1")
    starts = [i for i, m in enumerate(messages) if is_question(m)]
    if len(starts) <= keep_questions:
        return list(messages)
    kept = messages[starts[-keep_questions]:]
    cleaned = []
    for message in kept:
        content = message["content"]
        if message["role"] == "assistant" and not isinstance(content, str):
            content = [b for b in content if _block_type(b) not in THINKING_TYPES]
        cleaned.append({"role": message["role"], "content": content})
    return cleaned
