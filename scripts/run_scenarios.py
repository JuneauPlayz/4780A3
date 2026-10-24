"""Run the test scenarios end to end against the configured LLM and write a report.

    python scripts/run_scenarios.py              # all scenarios, real LLM (needs an API key)
    python scripts/run_scenarios.py --retrieval  # retrieval checks only, no API key needed
    python scripts/run_scenarios.py --only unknown-card

Writes scenarios/last_run.md and exits non-zero if any expectation fails.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from riftbound.explainer import explain  # noqa: E402
from riftbound.knowledge import KnowledgeBase, norm_rule  # noqa: E402

SCENARIOS = ROOT / "scenarios" / "scenarios.json"


def check_retrieval(kb: KnowledgeBase, sc: dict) -> list[str]:
    r = kb.retrieve(sc["question"] + " " + sc.get("clarification", ""), extra_text=sc.get("card_text", ""))
    problems = []
    rules = {norm_rule(n) for p in r.core for n in p["rule_ids"]}
    for n in sc.get("expect_retrieved_rules", []):
        if norm_rule(n) not in rules:
            problems.append(f"rule {n} not retrieved")
    ids = {p["id"] for p in r.passages}
    for s in sc.get("expect_retrieved_sources", []):
        if s not in ids:
            problems.append(f"source {s} not retrieved")
    names = {c["name"] for c in r.cards}
    for c in sc.get("expect_cards", []):
        if c not in names:
            problems.append(f"card {c} not recognized")
    if sc.get("expect_errata") and not any(c.get("errata") for c in r.cards):
        problems.append("errata text not applied")
    for u in sc.get("expect_unrecognized", []):
        if u not in r.unrecognized_names:
            problems.append(f"{u} not flagged as unrecognized")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval", action="store_true", help="only check retrieval (no LLM calls)")
    ap.add_argument("--only", help="run a single scenario id")
    ap.add_argument("--delay", type=float, default=4.0, help="seconds between LLM calls (free-tier rate limits)")
    args = ap.parse_args()

    kb = KnowledgeBase.load()
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    if args.only:
        scenarios = [s for s in scenarios if s["id"] == args.only]

    report = [f"# Scenario run ({time.strftime('%Y-%m-%d %H:%M')})", "", f"Core Rules {kb.manifest['core_rules']['last_updated']}", ""]
    failures = 0
    for i, sc in enumerate(scenarios):
        problems = check_retrieval(kb, sc)
        line = f"## {sc['id']}\n\n**Q:** {sc['question']}\n"
        if sc.get("clarification"):
            line += f"\n**Clarification:** {sc['clarification']}\n"
        if not args.retrieval:
            if i:
                time.sleep(args.delay)
            exp = explain(kb, sc["question"], sc.get("clarification", ""), sc.get("card_text", ""))
            if exp.error:
                problems.append(f"LLM error: {exp.error}")
            else:
                r = exp.result
                if r["status"] not in sc["expect_status"]:
                    problems.append(f"status {r['status']} not in {sc['expect_status']}")
                refs = [c.ref for c in exp.citations]
                if r["status"] == "answered":
                    for want in sc.get("expect_answer_citations", []):
                        if not any(ref.startswith(want) for ref in refs):
                            problems.append(f"answer does not cite {want}")
                if any("not in the indexed official sources" in w for w in exp.warnings):
                    problems.append("model produced an unverifiable citation (flagged and removed)")
                line += (
                    f"\n- status: **{r['status']}** (confidence {r['confidence']}, {exp.llm.provider} {exp.llm.model}, {exp.llm.seconds}s)"
                    f"\n- refined question: {r['refined_question']}"
                    f"\n- short answer: {r['short_answer'] or r['clarifying_question']}"
                    f"\n- citations: {', '.join(refs) or 'none'}"
                    f"\n- warnings: {'; '.join(exp.warnings) or 'none'}\n"
                )
        verdict = "PASS" if not problems else "FAIL: " + "; ".join(problems)
        failures += bool(problems)
        print(f"[{'PASS' if not problems else 'FAIL'}] {sc['id']}" + ("" if not problems else f"  ({'; '.join(problems)})"))
        report.append(line + f"\n**Result:** {verdict}\n")

    out = ROOT / "scenarios" / "last_run.md"
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"\n{len(scenarios) - failures}/{len(scenarios)} passed. Report: {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
