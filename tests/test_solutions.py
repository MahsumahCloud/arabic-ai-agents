import pytest
from conftest import load
from fakes import FakeClient, response, text, thinking, tool_use

ex1_1 = load("solutions/01/ex1_min_steps.py")
ex1_2 = load("solutions/01/ex2_ask_brief.py")
ex2_1 = load("solutions/02/ex1_unit_converter.py")
ex2_2 = load("solutions/02/ex2_audit_approver.py")
ex3_1 = load("solutions/03/ex1_trim_memory.py")
ex3_2 = load("solutions/03/ex2_require_citations.py")
agent_mod = load("lessons/03/research_agent.py")


def test_min_steps_theory_matches_measurement():
    assert ex1_1.theoretical_min_steps(1, 1000) == 10
    assert ex1_1.measured_min_steps(1, 1000) == 10


def test_ask_brief():
    client = FakeClient([response(text("جواب قصير."))])
    assert ex1_2.ask_brief(client, "؟") == ("جواب قصير.", "end_turn")
    assert client.requests[0]["system"] == ex1_2.BRIEF_SYSTEM


@pytest.mark.parametrize(
    "value,src,dst,expected",
    [(100, "c", "f", "212"), (10, "km", "mi", "6.214"), (1, "lb", "kg", "0.4536"), (5, "kg", "kg", "5")],
)
def test_unit_converter(tmp_path, value, src, dst, expected):
    box = ex2_1.ExtendedToolBox(tmp_path)
    result = box.run("unit_converter", {"value": value, "from_unit": src, "to_unit": dst})
    assert not result.is_error and result.content == expected


def test_unit_converter_rejects_bad_units(tmp_path):
    box = ex2_1.ExtendedToolBox(tmp_path)
    assert box.run("unit_converter", {"value": 1, "from_unit": "km", "to_unit": "kg"}).is_error
    assert box.run("unit_converter", {"value": 1, "from_unit": "parsec", "to_unit": "km"}).is_error
    assert any(t["name"] == "unit_converter" for t in box.definitions)


def test_audit_approver():
    approver = ex2_2.AuditApprover(ask_human=lambda n, a: True)
    assert approver("delete_file", {"path": "plan.MD"}) is False
    assert approver("delete_file", {"path": "old.txt"}) is True
    assert [d[2] for d in approver.decisions] == [False, True]


def test_trim_history_cuts_at_questions_and_strips_thinking():
    history = [
        {"role": "user", "content": "س1"},
        {"role": "assistant", "content": [thinking(), tool_use("list_documents", {}, "t1")]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "..."}]},
        {"role": "assistant", "content": [thinking(), text("ج1")]},
        {"role": "user", "content": "س2"},
        {"role": "assistant", "content": [thinking(), text("ج2")]},
    ]
    trimmed = ex3_1.trim_history(history, keep_questions=1)
    assert trimmed[0] == {"role": "user", "content": "س2"}
    assert [b.type for b in trimmed[1]["content"]] == ["text"]
    assert ex3_1.trim_history(history, keep_questions=5) == history


def test_require_citations_retries_once():
    client = FakeClient([
        response(text("الجواب بلا مصدر.")),
        response(tool_use("search_documents", {"query": "الخط الكوفي"}), stop_reason="tool_use"),
        response(text("الكوفي من أقدم الخطوط [calligraphy.txt:3].")),
    ])
    agent = agent_mod.ResearchAgent(client)
    answer = ex3_2.ask_with_citations(agent, "ما أقدم الخطوط؟")
    assert answer.citations.ok
    assert len(client.requests) == 3
