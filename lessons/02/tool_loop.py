"""Lesson 02: the tool-use loop, written by hand.

Run (needs ANTHROPIC_API_KEY):
    python lessons/02/tool_loop.py "كم يساوي ١٥٪ من ٢٤٨٠؟ وما تاريخ اليوم في الرياض؟"

The loop:
  1. send the conversation + tool definitions to the model
  2. if the model stops with "tool_use": run each requested tool, send ALL
     results back in ONE user message, and go to 1
  3. otherwise stop, and say why
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tools import ToolBox, ask_in_terminal  # noqa: E402

DEFAULT_MODEL = "claude-opus-5-5"

SYSTEM = (
    "أنت مساعد عربي دقيق. استخدم الأدوات المتاحة بدلاً من التخمين: "
    "الحاسبة لكل عملية حسابية، وأداة التاريخ لكل سؤال عن اليوم أو الوقت، "
    "وأدوات الملفات لقراءة الملفات. إذا فشلت أداة فاشرح السبب للمستخدم بإيجاز. "
    "أجب بالعربية الفصحى."
)


def make_client():
    import anthropic

    return anthropic.Anthropic()


@dataclass
class LoopResult:
    text: str
    stop: str  # "done" | "max_steps" | "truncated" | "refused" | "unexpected:<reason>"
    steps: int
    messages: list = field(default_factory=list)


def _text_of(content) -> str:
    return "".join(block.text for block in content if block.type == "text")


def run_with_tools(
    client,
    user_prompt: str,
    toolbox: ToolBox,
    *,
    model: str | None = None,
    max_steps: int = 8,
    system: str = SYSTEM,
) -> LoopResult:
    model = model or os.environ.get("AGENT_MODEL", DEFAULT_MODEL)
    messages: list = [{"role": "user", "content": user_prompt}]

    for step in range(1, max_steps + 1):
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            system=system,
            tools=toolbox.definitions,
            output_config={"effort": os.environ.get("AGENT_EFFORT", "low")},
            messages=messages,
        )
        # Append the FULL content (text, tool_use and any thinking blocks),
        # unchanged. Never rewrite or drop earlier turns.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                outcome = toolbox.run(block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,  # must match the request
                        "content": outcome.content,
                        "is_error": outcome.is_error,
                    }
                )
            # All results of one turn go back together, in a single user message.
            messages.append({"role": "user", "content": results})
            continue

        text = _text_of(response.content)
        if response.stop_reason in ("end_turn", "stop_sequence"):
            return LoopResult(text, "done", step, messages)
        if response.stop_reason == "max_tokens":
            return LoopResult(text, "truncated", step, messages)
        if response.stop_reason == "refusal":
            return LoopResult(text, "refused", step, messages)
        return LoopResult(text, f"unexpected:{response.stop_reason}", step, messages)

    return LoopResult("", "max_steps", max_steps, messages)


def main(argv: list[str]) -> int:
    prompt = argv[1] if len(argv) > 1 else "كم يساوي ١٥٪ من ٢٤٨٠؟ وما تاريخ اليوم في الرياض؟"
    toolbox = ToolBox(approver=ask_in_terminal)
    result = run_with_tools(make_client(), prompt, toolbox)
    for name, args, outcome in toolbox.log:
        flag = "error" if outcome.is_error else "ok"
        print(f"[tool:{flag}] {name}({args}) -> {outcome.content[:80]}")
    print(f"\n[stop: {result.stop}, steps: {result.steps}]\n")
    print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
