"""Riftbound Rules Explainer - Streamlit UI.

Run:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from riftbound import config, diagram, llm
from riftbound.explainer import explain
from riftbound.knowledge import KnowledgeBase

st.set_page_config(page_title="Riftbound Rules Explainer", page_icon="📜", layout="wide")

EXAMPLES = [
    ("Combat damage split",
     "I attack a battlefield with one 5 Might unit. My opponent has two 3 Might units defending there. "
     "Can I assign 3 damage to one and 2 to the other, or must it be split differently?"),
    ("Respond to a spell (ambiguous)",
     "My opponent played a spell targeting my unit. Can I respond with one of my spells to save it?"),
    ("Errata: Elnuk Herd",
     "I played Elnuk Herd from face down. Can its play ability give +3 Might to Elnuk Herd itself?"),
    ("Scoring twice",
     "Can I score the same battlefield twice in one turn if I conquer it, leave, and conquer it again?"),
    ("Banned card?", "Is Called Shot allowed in my deck?"),
    ("Not in sources: 2028 rotation", "When Standard rotation starts in 2028, which sets will rotate out?"),
]

STATUS_BADGE = {
    "answered": ("✅ Answered from official sources", "green"),
    "needs_clarification": ("❓ Needs one more detail", "orange"),
    "not_supported": ("⚠️ The official sources don't settle this", "red"),
}


@st.cache_resource(show_spinner="Loading the official rules index...")
def load_kb() -> KnowledgeBase:
    return KnowledgeBase.load()


def set_question(q: str) -> None:
    st.session_state.question = q
    st.session_state.clarification = ""
    st.session_state.pop("explanation", None)


def use_option(opt: str) -> None:
    st.session_state.clarification = opt
    st.session_state.run = True


def version_banner(kb: KnowledgeBase) -> None:
    m = kb.manifest
    core = m["core_rules"]
    errata = [d for d in m["documents"] if d["kind"] == "errata"]
    newest_errata = max(errata, key=lambda d: d.get("date") or "") if errata else None
    st.info(
        f"**Rules version:** [Riftbound Core Rules]({core['url']}), last updated **{core['last_updated']}**, "
        f"effective **{core['effective_date']}** · {core['rules_indexed']:,} numbered rules indexed · "
        f"{m['counts']['cards']:,} official cards ({m['counts']['cards_with_errata']} with errata"
        + (f", newest: {newest_errata['title']} {newest_errata['date']}" if newest_errata else "")
        + f") · index refreshed {m['fetched_at'][:10]} from the [Rules Hub]({m['rules_hub']})",
        icon="📘",
    )


def sidebar(kb: KnowledgeBase) -> None:
    with st.sidebar:
        st.header("Setup")
        provider = llm.available_provider()
        if provider == "gemini":
            st.success(f"LLM: Google Gemini (`{config.GEMINI_MODEL}`)")
        elif provider == "groq":
            st.success(f"LLM: Groq (`{config.GROQ_MODEL}`)")
        else:
            st.error(
                "No API key found. Add `GEMINI_API_KEY=...` (or `GROQ_API_KEY=...`) to a `.env` file "
                "in the project folder and restart. Retrieval still works without a key."
            )
        st.toggle("Show the prompts sent to the model", key="show_prompts")

        st.header("Official sources indexed")
        for d in kb.manifest["documents"]:
            date = d.get("last_updated") or d.get("date") or ""
            st.markdown(f"- [{d.get('title') or d['kind']}]({d['url']}) {f'· {date}' if date else ''}")
        st.caption("Refresh after Riot updates the rules: `python -m riftbound.refresh`")

        st.header("Prompt patterns in use")
        st.markdown(
            "- **Persona**: a patient rules explainer\n"
            "- **Question Refinement**: restates your question and asks about missing details\n"
            "- **Visualization Generator**: structured steps/board drawn with Graphviz\n"
            "- **Template**: fixed JSON answer format"
        )


def render_cards(retrieval) -> None:
    if not (retrieval.cards or retrieval.ambiguous_names or retrieval.unrecognized_names):
        return
    with st.expander(f"Cards recognized ({len(retrieval.cards)})", expanded=False):
        for c in retrieval.cards:
            cols = st.columns([1, 4])
            if c.get("image"):
                cols[0].image(c["image"], width=130)
            cols[1].markdown(f"**{c['name']}** · {'/'.join(c['types'])} · {', '.join(c['sets'])}")
            cols[1].text(c["current_text"] or "(no rules text)")
            if c.get("errata"):
                cols[1].caption(f"Text updated by [{c['errata']['source_title']}]({c['errata']['url']}) ({c['errata']['date']}). Printed text: {c['errata']['old_text']}")
        for name, cands in retrieval.ambiguous_names.items():
            st.warning(f"“{name}” matches several official cards: {', '.join(cands)}")
        for name in retrieval.unrecognized_names:
            st.warning(f"“{name}” was not found in the official Card Gallery. Paste its text below the question if you have it.")


def render_passages(exp) -> None:
    with st.expander(f"Official passages retrieved for this question ({len(exp.retrieval.passages)})"):
        for p in exp.retrieval.passages:
            date = p.get("doc_version") or p.get("date") or ""
            page = f", p. {p['page']}" if p.get("page") else ""
            st.markdown(f"**[{p['title']}]({p['link']})** · {p['source_title']} ({date}{page}) · score {p['score']}")
            st.text(p["text"][:1500] + ("…" if len(p["text"]) > 1500 else ""))


def render_answer(exp) -> None:
    r = exp.result
    label, color = STATUS_BADGE[r["status"]]
    st.markdown(f"### :{color}[{label}]")
    if r["refined_question"]:
        st.markdown(f"**How I understood your question:** _{r['refined_question']}_")

    if r["status"] == "needs_clarification":
        st.warning(f"**{r['clarifying_question']}**")
        if r["missing_details"]:
            st.markdown("Missing details: " + "; ".join(r["missing_details"]))
        if r["clarifying_options"]:
            cols = st.columns(len(r["clarifying_options"]))
            for col, opt in zip(cols, r["clarifying_options"]):
                col.button(opt, on_click=use_option, args=(opt,), width="stretch")
        with st.form("clarify"):
            text = st.text_input("Or type the missing detail", value=st.session_state.get("clarification", ""))
            if st.form_submit_button("Answer with this detail"):
                use_option(text)
                st.rerun()
    elif r["status"] == "not_supported":
        if r["explanation"] or r["short_answer"]:
            st.markdown(r["short_answer"] or "")
            st.markdown(r["explanation"])
        if r["missing_details"]:
            st.markdown("**What is missing:** " + "; ".join(r["missing_details"]))
        if r["clarifying_question"]:
            st.markdown(f"**Follow-up:** {r['clarifying_question']}")

    if r["status"] == "answered":
        st.success(r["short_answer"] or "See the explanation below.")
        tabs = st.tabs(["Explanation", "Step by step", "Example", "Diagram"])
        with tabs[0]:
            st.markdown(r["explanation"])
            if r["terms"]:
                st.markdown("**Terms used**")
                for t in r["terms"]:
                    cit = t.get("resolved")
                    ref = f" ([{cit.ref}]({cit.link}))" if cit and cit.verified and cit.link else ""
                    st.markdown(f"- **{t['term']}**: {t['meaning']}{ref}")
        with tabs[1]:
            for i, s in enumerate(r["steps"], start=1):
                refs = " ".join(f"[{c.ref}]({c.link})" for c in s.get("resolved", []) if c.verified and c.link)
                st.markdown(f"**{i}. {s['title']}**  \n{s['detail']}" + (f"  \n<small>{refs}</small>" if refs else ""), unsafe_allow_html=True)
        with tabs[2]:
            st.markdown(r["example"] or "_No example given._")
        with tabs[3]:
            st.caption("Drawn by the app from the model's structured output. It illustrates the scenario as you described it; it is not an official ruling.")
            seq = diagram.sequence_dot(r["steps"])
            board = diagram.board_dot(r["board"])
            if board:
                st.graphviz_chart(board, width="stretch")
            if seq:
                st.graphviz_chart(seq)
            if not (seq or board):
                st.write("No diagram for this answer.")
        if r["assumptions"]:
            st.markdown("**Assumptions:** " + "; ".join(r["assumptions"]))

    if r["gameplay_vs_tournament"]:
        st.info(f"**Gameplay vs. tournament:** {r['gameplay_vs_tournament']}")

    if exp.citations:
        st.markdown("#### Sources cited")
        for c in exp.citations:
            note = "" if c.in_context or c.kind == "source" else " _(exists, but was not in the retrieved passages; double-check)_"
            link = f"[{c.ref}]({c.link})" if c.link else c.ref
            st.markdown(f"- {link}: {c.title}{(' · ' + c.supports) if c.supports else ''}{note}")
    for w in exp.warnings:
        st.warning(w, icon="⚠️")
    st.caption(
        f"Confidence: {r['confidence']} · {exp.llm.provider} `{exp.llm.model}` · {exp.llm.seconds}s · "
        "Not an official Riot ruling. For sanctioned events, a judge's call is final."
    )


def main() -> None:
    st.title("📜 Riftbound Rules Explainer")
    st.caption("Ask about a game situation in Riftbound: League of Legends Trading Card Game. Answers are grounded in Riot's official rules documents.")
    try:
        kb = load_kb()
    except FileNotFoundError as exc:
        st.error(f"{exc}")
        st.stop()
    version_banner(kb)
    sidebar(kb)

    st.session_state.setdefault("question", "")
    st.session_state.setdefault("clarification", "")

    st.markdown("**Try an example:**")
    cols = st.columns(3)
    for i, (label, q) in enumerate(EXAMPLES):
        cols[i % 3].button(label, key=f"ex{i}", on_click=set_question, args=(q,), width="stretch", help=q)

    st.text_area(
        "Describe the game situation",
        key="question",
        height=120,
        placeholder="e.g. My unit with Deflect is chosen by my opponent's spell. What happens?",
    )
    with st.expander("Card text (optional: paste the text of any card the app doesn't recognize)"):
        st.text_area("Card text", key="card_text", height=90, label_visibility="collapsed")
    if st.session_state.clarification:
        st.caption(f"Clarification included: {st.session_state.clarification}")

    submitted = st.button("Explain the ruling", type="primary")
    if submitted:
        st.session_state.clarification = ""
    if (submitted or st.session_state.pop("run", False)) and st.session_state.question.strip():
        with st.spinner("Finding the relevant official rules and asking the model..."):
            st.session_state.explanation = explain(
                kb,
                st.session_state.question,
                clarification=st.session_state.clarification,
                user_card_text=st.session_state.get("card_text", ""),
            )

    exp = st.session_state.get("explanation")
    if exp is None:
        return
    st.divider()
    if exp.error:
        st.error(exp.error)
        st.markdown("Retrieval still ran, so you can see which official passages would be sent to the model:")
    else:
        render_answer(exp)
    render_cards(exp.retrieval)
    render_passages(exp)
    if st.session_state.get("show_prompts"):
        with st.expander("Prompts sent to the model", expanded=True):
            st.markdown("**System prompt** (Persona, Grounding, Question Refinement, Visualization Generator, Template)")
            st.code(exp.system_prompt, language="markdown")
            st.markdown("**User prompt** (rules version + retrieved passages + card text + scenario)")
            st.code(exp.user_prompt, language="markdown")


main()
