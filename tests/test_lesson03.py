import pytest
from conftest import load
from fakes import FakeClient, response, text, thinking, tool_use, usage

corpus_mod = load("lessons/03/corpus.py")
costs = load("lessons/03/costs.py")
citations = load("lessons/03/citations.py")
agent_mod = load("lessons/03/research_agent.py")


# ---- corpus ---------------------------------------------------------------

def test_normalize_arabic():
    assert corpus_mod.normalize("إِنَّ الْمَدْرَسَةَ") == "ان المدرسه"
    assert corpus_mod.normalize("مستشفى ١٢٣") == "مستشفي 123"


def test_query_terms_drop_stopwords_and_article():
    assert corpus_mod.query_terms("ما هي مراحل ثمرة النخلة؟") == ["مراحل", "ثمره", "نخله"]


def test_search_finds_relevant_lines():
    corpus = corpus_mod.Corpus()
    hits = corpus.search("مراحل ثمرة النخلة")
    assert hits and hits[0].doc_id == "palm.txt"
    assert "الرطب" in hits[0].text


def test_read_ranges():
    corpus = corpus_mod.Corpus()
    rows = corpus.read("hijri.txt", 2, 3)
    assert [n for n, _ in rows] == [2, 3]
    with pytest.raises(ValueError):
        corpus.read("nope.txt")
    with pytest.raises(ValueError):
        corpus.read("hijri.txt", 50, 60)


# ---- costs ----------------------------------------------------------------

def test_cost_tracker_prices_opus():
    tracker = costs.CostTracker("claude-opus-5-5")
    cost = tracker.add(usage(input_tokens=1_000_000, output_tokens=100_000))
    assert cost == pytest.approx(4.00 + 2.00)
    tracker.add(usage(input_tokens=0, output_tokens=0, cache_write=1_000_000, cache_read=1_000_000))
    assert tracker.total_usd == pytest.approx(6.00 + 5.00 + 0.20)
    assert tracker.calls == 2


def test_cost_tracker_unknown_model_counts_tokens_only():
    tracker = costs.CostTracker("some-other-model")
    assert tracker.add(usage(500, 500)) == 0.0
    assert tracker.input_tokens == 500 and "unpriced" in tracker.summary()


# ---- citations --------------------------------------------------------------

def test_citations_are_checked_against_what_was_seen():
    corpus = corpus_mod.Corpus()
    answer = "معلومة [palm.txt:5] وأخرى [palm.txt:2-3] وثالثة [hijri.txt:99] ورابعة [solar.txt:2]"
    report = citations.check_citations(answer, corpus, {"palm.txt": {2, 3, 5}})
    assert [str(c) for c in report.valid] == ["[palm.txt:5]", "[palm.txt:2-3]"]
    assert [str(c) for c in report.invalid] == ["[hijri.txt:99]"]
    assert [str(c) for c in report.unseen] == ["[solar.txt:2]"]
    assert not report.ok


# ---- the agent --------------------------------------------------------------

def scripted_research_run():
    return [
        response(thinking(), tool_use("write_plan", {"steps": ["ابحث", "اقرأ", "أجب"]}), stop_reason="tool_use"),
        response(tool_use("search_documents", {"query": "مراحل ثمرة النخلة"}), stop_reason="tool_use"),
        response(tool_use("read_document", {"doc_id": "palm.txt", "start_line": 5, "end_line": 5}), stop_reason="tool_use"),
        response(text("تمر الثمرة بمراحل: الخلال ثم الرطب ثم التمر [palm.txt:5].")),
    ]


def test_agent_full_run_plans_reads_cites_and_costs():
    client = FakeClient(scripted_research_run())
    agent = agent_mod.ResearchAgent(client)
    answer = agent.ask("ما مراحل ثمرة النخلة؟")

    assert answer.stop == "done" and answer.steps == 4
    assert answer.plan == ["ابحث", "اقرأ", "أجب"]
    assert answer.citations.ok and [str(c) for c in answer.citations.valid] == ["[palm.txt:5]"]
    # 4 calls x (100 in, 50 out) on Opus 5.5 pricing
    assert answer.cost_usd == pytest.approx(4 * (100 * 4.00 + 50 * 20.00) / 1_000_000)
    search_result = client.requests[2]["messages"][-1]["content"][0]
    assert "palm.txt:5:" in search_result["content"]


def test_agent_remembers_the_conversation():
    client = FakeClient(scripted_research_run() + [response(text("سؤالك الأول كان عن النخلة."))])
    agent = agent_mod.ResearchAgent(client)
    agent.ask("ما مراحل ثمرة النخلة؟")
    agent.ask("عن ماذا سألتك أولاً؟")
    history = client.requests[-1]["messages"]
    assert history[0]["content"] == "ما مراحل ثمرة النخلة؟"
    assert history[-1]["content"] == "عن ماذا سألتك أولاً؟"
    # earlier assistant turns are replayed unchanged, thinking block included
    assert history[1]["content"][0].type == "thinking"


def test_agent_stops_at_step_limit():
    endless = [response(tool_use("list_documents", {"x": 1} if i % 2 else {}), stop_reason="tool_use") for i in range(3)]
    agent = agent_mod.ResearchAgent(FakeClient(endless), max_steps=3, max_repeats=99)
    assert agent.ask("؟").stop == "max_steps"


def test_agent_stops_on_budget():
    expensive = usage(input_tokens=200_000, output_tokens=0)  # $0.80 on Opus 5.5
    client = FakeClient([response(tool_use("list_documents", {}), stop_reason="tool_use", tokens=expensive)])
    agent = agent_mod.ResearchAgent(client, max_cost_usd=0.50)
    answer = agent.ask("؟")
    assert answer.stop == "budget" and len(client.requests) == 1


def test_agent_detects_repeated_calls_and_keeps_history_valid():
    same = lambda: response(tool_use("search_documents", {"query": "نخلة"}), tool_use("list_documents", {}), stop_reason="tool_use")
    client = FakeClient([same(), same(), same()])
    agent = agent_mod.ResearchAgent(client, max_repeats=2)
    answer = agent.ask("؟")
    assert answer.stop == "loop_detected"
    last_results = agent.messages[-1]["content"]
    assert len(last_results) == 2 and all(r["is_error"] for r in last_results)


def test_agent_tool_errors_go_back_to_the_model():
    client = FakeClient([
        response(tool_use("read_document", {"doc_id": "missing.txt"}), stop_reason="tool_use"),
        response(text("لم أجد في المستندات ما يجيب عن ذلك.")),
    ])
    agent = agent_mod.ResearchAgent(client)
    answer = agent.ask("؟")
    error = client.requests[1]["messages"][-1]["content"][0]
    assert error["is_error"] is True and "unknown document" in error["content"]
    assert answer.stop == "done" and answer.citations.summary() == "no citations"


@pytest.mark.parametrize("reason,expected", [("max_tokens", "truncated"), ("refusal", "refused")])
def test_agent_other_stops(reason, expected):
    agent = agent_mod.ResearchAgent(FakeClient([response(text("..."), stop_reason=reason)]))
    assert agent.ask("؟").stop == expected


def test_reset_forgets_everything():
    agent = agent_mod.ResearchAgent(FakeClient(scripted_research_run()))
    agent.ask("ما مراحل ثمرة النخلة؟")
    agent.reset()
    assert agent.messages == [] and not agent.seen
