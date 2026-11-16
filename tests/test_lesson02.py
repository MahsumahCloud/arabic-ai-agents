from datetime import datetime

import pytest
from conftest import load
from fakes import FakeClient, response, text, tool_use

tools = load("lessons/02/tools.py")
loop = load("lessons/02/tool_loop.py")


@pytest.fixture
def sandbox(tmp_path):
    (tmp_path / "a.txt").write_text("سطر أول\nسطر ثانٍ", encoding="utf-8")
    (tmp_path / "secret.py").write_text("print('no')", encoding="utf-8")
    return tmp_path


def fixed_now(tz):
    return datetime(2026, 11, 16, 9, 30, tzinfo=tz)


# ---- calculator -----------------------------------------------------------

@pytest.mark.parametrize(
    "expr,expected",
    [("2+3*4", "14"), ("(1250 * 0.15) + 30", "217.5"), ("٢٤٨٠ * ٠٫١٥", "372"), ("-2**3", "-8"), ("7 // 2", "3")],
)
def test_calculator(expr, expected):
    assert tools.calculator(expr) == expected


@pytest.mark.parametrize("expr", ["__import__('os')", "open('x')", "2**10000", "((9**99)**99)**99", "1/0", "a+1", "", "9" * 300])
def test_calculator_rejects_unsafe_or_invalid(expr):
    with pytest.raises(ValueError):
        tools.calculator(expr)


# ---- validation and toolbox -----------------------------------------------

def test_validate_input():
    schema = tools.TOOL_DEFINITIONS[0]["input_schema"]
    assert tools.validate_input(schema, {"expression": "1+1"}) is None
    assert "missing" in tools.validate_input(schema, {})
    assert "unexpected" in tools.validate_input(schema, {"expression": "1", "x": 2})
    assert "must be string" in tools.validate_input(schema, {"expression": 5})
    assert tools.validate_input(schema, "not a dict") is not None


def test_datetime_tool(sandbox):
    box = tools.ToolBox(sandbox, now=fixed_now)
    result = box.run("get_current_datetime", {"timezone": "Asia/Riyadh"})
    assert not result.is_error
    assert result.content.startswith("2026-11-16T09:30:00+03:00")
    assert box.run("get_current_datetime", {"timezone": "Mars/Base"}).is_error


def test_read_file_stays_in_sandbox(sandbox):
    box = tools.ToolBox(sandbox)
    assert box.run("read_file", {"path": "a.txt"}).content.startswith("سطر أول")
    for bad in ["../outside.txt", "/etc/passwd", "secret.py", "missing.txt"]:
        assert box.run("read_file", {"path": bad}).is_error, bad
    assert box.run("list_files", {}).content == "a.txt"


def test_dangerous_tool_needs_approval(sandbox):
    denied = tools.ToolBox(sandbox)  # default approver denies everything
    result = denied.run("delete_file", {"path": "a.txt"})
    assert result.is_error and (sandbox / "a.txt").exists()

    approved = tools.ToolBox(sandbox, approver=lambda name, args: True)
    assert not approved.run("delete_file", {"path": "a.txt"}).is_error
    assert not (sandbox / "a.txt").exists()


def test_unknown_tool_is_an_error_not_a_crash(sandbox):
    assert tools.ToolBox(sandbox).run("rm_rf", {}).is_error


# ---- the loop ---------------------------------------------------------------

def test_loop_runs_tools_and_returns_answer(sandbox):
    calc = tool_use("calculator", {"expression": "2480*0.15"}, "toolu_a")
    date = tool_use("get_current_datetime", {}, "toolu_b")
    client = FakeClient([
        response(text("سأحسب."), calc, date, stop_reason="tool_use"),
        response(text("الناتج 372 [تم]")),
    ])
    box = tools.ToolBox(sandbox, now=fixed_now)
    result = loop.run_with_tools(client, "سؤال", box)

    assert result.stop == "done" and result.steps == 2
    assert result.text == "الناتج 372 [تم]"
    second = client.requests[1]
    # assistant turn appended unchanged, then ONE user message with BOTH results
    assert second["messages"][1]["role"] == "assistant"
    results = second["messages"][2]["content"]
    assert [r["tool_use_id"] for r in results] == ["toolu_a", "toolu_b"]
    assert results[0]["content"] == "372" and results[0]["is_error"] is False
    assert second["tools"] == tools.TOOL_DEFINITIONS
    assert "tool_choice" not in second


def test_loop_reports_tool_errors_to_the_model(sandbox):
    client = FakeClient([
        response(tool_use("read_file", {"path": "../x.txt"}, "t1"), stop_reason="tool_use"),
        response(text("لا أستطيع قراءة هذا الملف.")),
    ])
    result = loop.run_with_tools(client, "اقرأ", tools.ToolBox(sandbox))
    tool_result = client.requests[1]["messages"][2]["content"][0]
    assert tool_result["is_error"] is True and "outside" in tool_result["content"]
    assert result.stop == "done"


def test_loop_stops_at_max_steps(sandbox):
    endless = [response(tool_use("list_files", {}), stop_reason="tool_use") for _ in range(3)]
    result = loop.run_with_tools(FakeClient(endless), "x", tools.ToolBox(sandbox), max_steps=3)
    assert result.stop == "max_steps" and result.steps == 3


@pytest.mark.parametrize("reason,expected", [("max_tokens", "truncated"), ("refusal", "refused"), ("pause_turn", "unexpected:pause_turn")])
def test_loop_other_stop_reasons(sandbox, reason, expected):
    result = loop.run_with_tools(FakeClient([response(text("..."), stop_reason=reason)]), "x", tools.ToolBox(sandbox))
    assert result.stop == expected


def test_tools_are_not_run_when_answer_was_truncated(sandbox):
    approved = tools.ToolBox(sandbox, approver=lambda n, a: True)
    client = FakeClient([response(tool_use("delete_file", {"path": "a.txt"}), stop_reason="max_tokens")])
    loop.run_with_tools(client, "x", approved)
    assert (sandbox / "a.txt").exists()
