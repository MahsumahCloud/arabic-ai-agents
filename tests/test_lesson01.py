import pytest
from conftest import load
from fakes import FakeClient, response, text, thinking

first_call = load("lessons/01/first_call.py")
toy = load("lessons/01/agent_loop_toy.py")


def test_ask_sends_a_well_formed_request():
    client = FakeClient([response(thinking(), text("مرحباً"))])
    answer = first_call.ask(client, "سلام", system="كن موجزاً")
    assert answer == "مرحباً"
    request = client.requests[0]
    assert request["model"] == "claude-opus-5-5"
    assert request["messages"] == [{"role": "user", "content": "سلام"}]
    assert request["system"] == "كن موجزاً"
    assert request["output_config"] == {"effort": "low"}
    assert "thinking" not in request  # Opus 5.5 always thinks; do not send a thinking config


def test_model_and_effort_come_from_env(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("AGENT_EFFORT", "medium")
    client = FakeClient([response(text("ok"))])
    first_call.ask(client, "q")
    assert client.requests[0]["model"] == "claude-sonnet-5-5"
    assert client.requests[0]["output_config"] == {"effort": "medium"}


def test_ask_handles_refusal_and_truncation():
    assert "declined" in first_call.ask(FakeClient([response(stop_reason="refusal")]), "q")
    cut = first_call.ask(FakeClient([response(text("نصف"), stop_reason="max_tokens")]), "q")
    assert cut.startswith("نصف") and "max_tokens" in cut


@pytest.mark.parametrize("secret", [1, 50, 73, 100])
def test_toy_agent_always_finds_the_number(secret):
    solved, history = toy.run(toy.NumberEnvironment(secret))
    assert solved
    assert history[-1] == (secret, "correct")
    assert len(history) <= 7  # ceil(log2(101))


def test_toy_agent_respects_step_limit():
    solved, history = toy.run(toy.NumberEnvironment(1), max_steps=2)
    assert not solved and len(history) == 2


def test_environment_rejects_secret_outside_range():
    with pytest.raises(ValueError):
        toy.NumberEnvironment(0)
