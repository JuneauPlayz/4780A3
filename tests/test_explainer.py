"""Pipeline tests with a stub LLM, so they run without an API key."""

import pytest

from riftbound import diagram, prompts
from riftbound.explainer import explain, normalize
from riftbound.knowledge import KnowledgeBase
from riftbound.llm import LLMResult, MissingKeyError, parse_json

QUESTION = "I attack with one 5 Might unit into two 3 Might defenders. Can I assign 3 and 2?"


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


def stub(data):
    calls = []

    def llm(system, user):
        calls.append((system, user))
        return LLMResult(data, "{}", "stub", "stub-model", 0.0)

    llm.calls = calls
    return llm


def test_prompts_contain_patterns_version_and_passages(kb):
    llm = stub({"status": "answered", "short_answer": "x"})
    explain(kb, QUESTION, llm=llm)
    system, user = llm.calls[0]
    for block in ("## Persona", "## Question Refinement", "## Visualization Generator", "## Output template", "## Grounding rules"):
        assert block in system
    assert "patient Riftbound rules explainer" in system
    assert "last updated 2026-10-09" in user or kb.manifest["core_rules"]["last_updated"] in user
    assert "467.2.c.3." in user  # the retrieved Core Rules passage text is in the prompt
    assert QUESTION in user


def test_invented_rule_numbers_are_flagged_not_linked(kb):
    llm = stub(
        {
            "status": "answered",
            "short_answer": "Assign lethal first [CR 467.2.c.3].",
            "explanation": "See [CR 467.2.c.3] and [CR 999.9] and [S9].",
            "steps": [{"title": "Assign", "detail": "d", "citations": ["CR 467.2.c.3", "CR 901.1"]}, {"title": "Deal", "detail": "d", "citations": []}],
            "citations": [{"ref": "CR 467.2.c.3", "supports": "lethal first"}],
            "confidence": "high",
        }
    )
    exp = explain(kb, QUESTION, llm=llm)
    refs = {c.ref for c in exp.citations}
    assert "CR 467.2.c.3" in refs
    assert "CR 999.9" not in refs and "CR 901.1" not in refs
    assert "[⚠ CR 999.9 not found]" in exp.result["explanation"]
    assert "#page=" in exp.result["short_answer"]
    assert exp.result["steps"][0]["citations"] == ["CR 467.2.c.3"]
    assert any("999.9" in w for w in exp.warnings)
    assert "901.1" not in diagram.sequence_dot(exp.result["steps"])


def test_citation_with_trailing_commentary_still_resolves(kb):
    llm = stub({"status": "answered", "citations": [{"ref": "CR 467 (definition in the rule text)", "supports": "x"}]})
    exp = explain(kb, QUESTION, llm=llm)
    assert [c.ref for c in exp.citations] == ["CR 467"]
    assert not exp.warnings


def test_wrong_rulebook_prefix_resolves_to_the_passage_given(kb):
    q = "When Standard rotation starts in 2028, which sets will rotate out?"
    exp = explain(kb, q, llm=stub({"status": "answered", "short_answer": "See [CR 601.3.b].", "citations": [{"ref": "CR 601.3.b", "supports": "x"}]}))
    assert [c.ref for c in exp.citations] == ["TR 601.3.b"]
    assert "[TR 601.3.b]" in exp.result["short_answer"]
    assert not exp.warnings


def test_answer_without_valid_citation_is_downgraded(kb):
    exp = explain(kb, QUESTION, llm=stub({"status": "answered", "short_answer": "Yes [CR 999.1].", "confidence": "high"}))
    assert exp.result["confidence"] == "low"
    assert any("no verifiable citation" in w for w in exp.warnings)


def test_clarification_shape_and_followup_is_sent(kb):
    llm = stub({"status": "needs_clarification", "missing_details": ["your spell's timing keyword"], "clarifying_options": ["Reaction", "Action"]})
    exp = explain(kb, "Can I respond to their spell?", clarification="My spell has [Reaction].", llm=llm)
    assert exp.result["status"] == "needs_clarification"
    assert "timing keyword" in exp.result["clarifying_question"]
    assert "PLAYER'S ANSWER TO YOUR CLARIFYING QUESTION" in llm.calls[0][1]
    assert "My spell has [Reaction]." in llm.calls[0][1]


def test_unknown_card_is_called_out_in_prompt(kb):
    llm = stub({"status": "needs_clarification"})
    explain(kb, "If my Shadow Mirage King copies a legend, do I get its abilities?", llm=llm)
    assert "NOT in the official Card Gallery" in llm.calls[0][1]
    assert "Shadow Mirage King" in llm.calls[0][1]


def test_user_card_text_is_marked_unverified(kb):
    llm = stub({"status": "answered"})
    explain(kb, "What does my card do?", user_card_text="Shadow Mirage King: When I attack, draw 1.", llm=llm)
    assert "USER-SUPPLIED CARD TEXT" in llm.calls[0][1]


def test_bad_status_normalizes_to_not_supported():
    assert normalize({"status": "maybe"})["status"] == "not_supported"
    assert normalize({"status": "ANSWERED", "steps": ["one"]})["steps"][0]["detail"] == "one"


def test_missing_key_reports_error(kb, monkeypatch):
    def no_key(system, user):
        raise MissingKeyError("No LLM API key found.")

    exp = explain(kb, QUESTION, llm=no_key)
    assert exp.error and exp.retrieval.core  # retrieval still ran


def test_parse_json_tolerates_fences():
    assert parse_json('```json\n{"status": "answered"}\n```') == {"status": "answered"}
    assert parse_json('Here you go: {"a": 1} thanks') == {"a": 1}


def test_board_diagram_drops_moves_to_unknown_zones():
    board = {
        "zones": [{"name": "Your base", "owner": "you", "objects": [{"label": 'Unit "A" (3 Might)', "owner": "you"}]},
                  {"name": "Battlefield A", "owner": "shared", "objects": []}],
        "moves": [{"object": "Unit A", "from": "Your base", "to": "Battlefield A"}, {"object": "X", "from": "Mars", "to": "Battlefield A"}],
    }
    dot = diagram.board_dot(board)
    assert dot.count("->") == 1
    assert '\\"A\\"' in dot  # quotes escaped
    assert diagram.board_dot(None) is None
    assert diagram.sequence_dot([{"title": "only one"}]) is None


def test_system_prompt_is_built_from_named_blocks():
    system = prompts.build_system_prompt()
    for block in prompts.SYSTEM_PROMPT_BLOCKS:
        assert block in system
