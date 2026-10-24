"""Checks against the committed index in data/ (no network, no API key)."""

import json
from pathlib import Path

import pytest

from riftbound.knowledge import KnowledgeBase, norm_rule

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def kb():
    return KnowledgeBase.load()


def test_manifest_records_version_and_sources(kb):
    core = kb.manifest["core_rules"]
    assert core["last_updated"] and core["effective_date"] >= core["last_updated"]
    assert core["url"].endswith(".pdf")
    kinds = {d["kind"] for d in kb.manifest["documents"]}
    assert {"core_rules", "tournament_rules", "patch_notes", "errata", "faq", "legality", "cards"} <= kinds
    assert kb.manifest["counts"]["unmatched_errata"] == []


def test_rule_numbers_exist_and_link_to_pdf_page(kb):
    for n in ("001", "467.2.c.3", "811", "472"):
        assert kb.rule_exists("core_rules", n), n
    assert not kb.rule_exists("core_rules", "999.9")
    assert "#page=" in kb.rule_link("core_rules", "467.2.c.3")


def test_errata_text_wins_over_printed_text(kb):
    elnuk = kb.card_by_key["elnuk herd"]
    assert elnuk["errata"] is not None
    assert "give a friendly unit" in elnuk["current_text"]
    assert "another friendly unit" in elnuk["printed_text"]
    assert "Errata" in kb.card_summary(elnuk)


def test_card_detection(kb):
    cards, ambiguous, unknown = kb.find_cards("If my Shadow Mirage King copies a legend, and Jinx, Rebel attacks")
    assert [c["name"] for c in cards] == ["Jinx, Rebel"]
    assert unknown == ["Shadow Mirage King"]
    _, ambiguous, _ = kb.find_cards("When I attack with Ahri what happens?")
    assert "Ahri" in ambiguous and len(ambiguous["Ahri"]) > 1


def test_rule_number_in_question_is_pinned(kb):
    r = kb.retrieve("What does rule 467.2.c.4 mean?")
    assert "467.2.c.4" in {norm_rule(n) for n in r.core[0]["rule_ids"]}


SCENARIOS = json.loads((ROOT / "scenarios" / "scenarios.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_retrieval(kb, sc):
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from run_scenarios import check_retrieval

    assert check_retrieval(kb, sc) == []
