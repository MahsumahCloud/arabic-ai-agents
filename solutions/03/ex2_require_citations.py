"""Solution 03-2: if an answer has no valid citations, ask the agent once more."""

from __future__ import annotations

NOT_FOUND = "لم أجد في المستندات"
RETRY_PROMPT = (
    "إجابتك السابقة لا تحتوي على مصادر صحيحة. أعد الإجابة مع ذكر المصدر بعد كل معلومة "
    "بالصيغة [اسم_الملف:رقم_السطر]، واعتمد فقط على أسطر قرأتها بالأدوات."
)


def ask_with_citations(agent, question: str, retries: int = 1):
    answer = agent.ask(question)
    attempts = 0
    while (
        answer.stop == "done"
        and not answer.citations.ok
        and NOT_FOUND not in answer.text
        and attempts < retries
    ):
        attempts += 1
        answer = agent.ask(RETRY_PROMPT)
    return answer
