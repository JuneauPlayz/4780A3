"""Drive the Streamlit UI headlessly with a stub LLM (no API key, no browser)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from riftbound import explainer
from riftbound.llm import LLMResult

APP = str(Path(__file__).resolve().parent.parent / "app.py")

ANSWER = {
    "status": "answered",
    "refined_question": "During the combat damage step, must the attacker assign lethal damage to one defender first?",
    "short_answer": "No, you must assign 3 (lethal) to one unit first, then 2 to the other [CR 467.2.c.3].",
    "explanation": "Lethal damage must be assigned in full before moving on [CR 467.2.c.3].",
    "steps": [
        {"title": "Sum Might", "detail": "Attacker total is 5 [CR 467.2.a].", "citations": ["CR 467.2.a"]},
        {"title": "Assign lethal first", "detail": "3 to the first defender.", "citations": ["CR 467.2.c.3"]},
    ],
    "example": "5 damage vs two 3 Might units: 3 + 2.",
    "terms": [{"term": "Lethal damage", "meaning": "damage at least equal to Might", "citation": "CR 467.2.c.2"}],
    "citations": [{"ref": "CR 467.2.c.3", "supports": "lethal first"}],
    "confidence": "high",
    "board": {"zones": [{"name": "Battlefield", "owner": "shared", "objects": [{"label": "Attacker (5 Might)", "owner": "you"}]}]},
}


def run_with(monkeypatch, data, question="I attack with 5 Might into two 3 Might units."):
    monkeypatch.setattr(explainer, "generate_json", lambda s, u: LLMResult(data, "{}", "stub", "stub-model", 0.1))
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.text_area(key="question").input(question)
    next(b for b in at.button if b.label == "Explain the ruling").click()
    return at.run()


def test_app_loads_with_version_banner():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert any("Rules version" in i.value for i in at.info)


def test_answer_renders_with_citations(monkeypatch):
    at = run_with(monkeypatch, ANSWER)
    assert not at.exception
    assert any("467.2.c.3" in s.value for s in at.success)
    assert any("Sources cited" in m.value for m in at.markdown)


def test_clarification_renders_options(monkeypatch):
    at = run_with(
        monkeypatch,
        {"status": "needs_clarification", "clarifying_question": "Does your spell have Reaction?", "clarifying_options": ["Yes, Reaction", "No, Action"]},
    )
    assert not at.exception
    assert any("Does your spell have Reaction?" in w.value for w in at.warning)
    assert any(b.label == "Yes, Reaction" for b in at.button)
