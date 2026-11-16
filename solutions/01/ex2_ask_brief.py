"""Solution 01-2: a helper that asks for a short Arabic answer and reports why it stopped."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lessons" / "01"))
from first_call import extract_text, get_model  # noqa: E402

BRIEF_SYSTEM = (
    "أجب بالعربية الفصحى في جملتين أو ثلاث جمل فقط. "
    "إذا لم تكن متأكداً من المعلومة فقل ذلك صراحة."
)


def ask_brief(client, question: str) -> tuple[str, str]:
    """Return (answer_text, stop_reason)."""
    response = client.messages.create(
        model=get_model(),
        max_tokens=16000,
        output_config={"effort": "low"},
        system=BRIEF_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return extract_text(response), response.stop_reason
