# Riftbound Rules Explainer

A small web app for players of **Riftbound: League of Legends Trading Card Game**. A player types a game situation in plain English. The app finds the relevant passages in Riot's official rules, sends them to an LLM with prompts built from course prompt patterns, and shows:

- a short ruling and a plain-language explanation,
- a step-by-step walk through the order of events,
- a small concrete example,
- definitions of the game terms used,
- **clickable citations with exact rule numbers**, each linked to the right page of the official Core Rules PDF,
- a deterministic diagram (sequence and board) drawn from structured model output,
- a focused clarifying question instead of a guess when a decisive detail is missing.

CS4680 Prompt Engineering, Assignment 3 (AI Assistant Project).

> Not affiliated with or endorsed by Riot Games. Riftbound and League of Legends are trademarks of Riot Games, Inc. The app links to and quotes Riot's public rules documents for educational use. A judge's ruling at a sanctioned event is always final.

---

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env
# edit .env and set GEMINI_API_KEY=...   (or GROQ_API_KEY=...)
streamlit run app.py
```

Open http://localhost:8501.

**API key.** Set **one** of these in `.env` (gitignored) or in your environment:

| Variable | Provider | Free key |
|---|---|---|
| `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) | Google Gemini, default model `gemini-2.5-flash` | https://aistudio.google.com/apikey |
| `GROQ_API_KEY` | Groq, default model `openai/gpt-oss-120b` | https://console.groq.com/keys |

With `LLM_PROVIDER=auto` (the default), the app uses Gemini if its key is set, otherwise Groq. If the configured model is unavailable, it tries a few known fallbacks (see `riftbound/llm.py`). You can override `GEMINI_MODEL` / `GROQ_MODEL` in `.env`.

Without a key, the app still starts and runs retrieval, so you can see which official passages would go to the model. It shows the exact variable to set.

The rules index is already built and committed in `data/`, so the app works right after cloning. Rebuild it any time with `python -m riftbound.refresh` (see below).

---

## Rules sources and version

Everything starts at Riot's official **Rules Hub**: https://playriftbound.com/en-us/rules-hub/. The refresh script reads that page and downloads whatever it currently links to. It also finds the official FAQ articles from the Rules & Releases news listing, because the hub does not link them.

Index as of **2026-10-23**:

| Source | Version / date | Used for |
|---|---|---|
| [Riftbound Core Rules (PDF)](https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/5c7946f7c3b8c6e0faff85ab6dadc6d2e721ea94.pdf) | **Last updated 2026-10-09, effective 2026-10-16** (per the Radiance patch notes); 142 pages, 2,494 numbered rules | Gameplay rules (primary authority) |
| [Riftbound Tournament Rules (PDF)](https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/861752822d217edf37d9febaeaf77a7d924c1bb6.pdf) | Last updated 2026-10-09 | Event procedure (separate from gameplay) |
| [Rules Hub: Constructed Format Legality](https://playriftbound.com/en-us/rules-hub/) | Last updated 2026-09-18 | Banned cards / format legality |
| Patch notes: [Core](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-core-rules-patch-notes/) (2025-10-24), [Spiritforged](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-core-rules-spiritforged-patch-notes/) (2025-12-05), [Unleashed](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-core-rules-unleashed-patch-notes/) (2026-03-30), [Vendetta](https://playriftbound.com/en-us/news/announcements/core-rules-vendetta-patch-notes/) (2026-07-17), [Radiance](https://playriftbound.com/en-us/news/announcements/core-rules-radiance-patch-notes-effective-october-16-2026/) (2026-10-09, effective 2026-10-16) | | Official rulings and explanations |
| FAQs: [Origins](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-origins-faq/) (2025-10-16), [Spiritforged](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-spiritforged-faq/) (2026-01-14), [Unleashed](https://playriftbound.com/en-us/news/rules-and-releases/unleashed-rules-faq-and-clarifications/) (2026-04-29), [Vendetta](https://playriftbound.com/en-us/news/rules-and-releases/vendetta-rules-faq-and-clarifications/) (2026-08-14) | | Official rulings |
| Errata: [Origins](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-origins-card-errata/) (2025-10-28), [Spiritforged](https://playriftbound.com/en-us/news/rules-and-releases/riftbound-spiritforged-errata/) (2026-01-14), [Unleashed](https://playriftbound.com/en-us/news/rules-and-releases/unleashed-errata-updates/) (2026-04-03), [Vendetta](https://playriftbound.com/en-us/news/announcements/vendetta-errata-updates/) (2026-07-23), [Radiance](https://playriftbound.com/en-us/news/announcements/radiance-errata-updates/) (2026-10-09) | 67 cards | Current card wording |
| [Official Card Gallery](https://playriftbound.com/en-us/card-gallery/) | 1,104 unique cards | Card text (printed wording) |

`data/manifest.json` records each document's URL, date, page count, SHA-256 hash, and fetch time. The app shows the version banner on every page.

**Precedence.** The app follows this order, which is also written into the prompt:

1. Current card text, with errata applied. Core Rule 002: card text supersedes rules text.
2. The current Core Rules.
3. The newest patch notes and FAQs.
4. Older FAQs.

The Card Gallery shows **printed** text. For example, Elnuk Herd still reads "give *another* friendly unit +3 Might" there, but the 2026-10-09 Radiance errata changed it to "give *a* friendly unit". The refresh applies every errata on top of the gallery, oldest first, so the newest wording wins. The UI and prompt show both the current and the printed text. Only the newest Core Rules PDF is indexed, so an older rules version can never be retrieved. FAQ and patch-note rulings are labeled with their date, and the prompt warns that rule numbers inside older articles may be outdated.

**Gameplay vs. tournament.** Core Rules passages and Tournament Rules/legality passages are labeled separately, and the answer has a dedicated "Gameplay vs. tournament" field. For example, *Called Shot* is playable under the Core Rules but banned in sanctioned Constructed.

### Updating the rules when Riot publishes changes

```bash
python -m riftbound.refresh
```

This re-downloads the Rules Hub, follows its current links (new Core Rules PDF, new patch notes or errata), re-parses everything, rewrites `data/`, and prints whether the Core Rules version changed:

```
Core Rules last updated 2026-10-09, effective 2026-10-16
790 passages, 1104 cards (67 with errata)
Core Rules CHANGED: 2026-10-09 -> 2026-12-??     (only when Riot updates it)
```

Then restart the app, run `pytest` (to confirm the new documents parsed), and commit `data/`. The originals are kept in `data/raw/` (gitignored). `python -m riftbound.refresh --offline` re-parses them without downloading. If Riot changes the Rules Hub layout so a PDF link can't be found, the refresh stops with a clear error instead of silently indexing nothing.

---

## How it works

```
question ──► retrieval (riftbound/knowledge.py)
             • BM25 keyword search over 790 passages, each keeping its exact rule numbers + PDF page
             • exact rule numbers in the question are always included ("rule 467.2.c.4")
             • card names matched against the official gallery; errata applied; keywords on
               those cards ([Hidden], [Reaction]) are added to the search
             • unknown card-like names ("Shadow Mirage King") and ambiguous names ("Ahri") are flagged
         ──► prompt (riftbound/prompts.py): pattern blocks + rules version + passages + card text
         ──► LLM (riftbound/llm.py): Gemini or Groq, JSON output
         ──► citation check (riftbound/explainer.py): every rule number is looked up in the index;
             real ones become links to the PDF page, invented ones are flagged and dropped
         ──► Streamlit UI (app.py) + deterministic Graphviz diagram (riftbound/diagram.py)
```

**Retrieval.** `riftbound/parsing.py` splits the Core Rules PDF into numbered rules, using the pattern `467.2.c.4. text…`. Each top-level rule and its sub-rules become one passage, split at sub-rule boundaries if it is long. Short neighboring rules are merged. Every passage keeps its exact rule numbers and the PDF page of each rule. Patch notes and FAQs are split into Q&A passages, and errata into per-card passages. Search is plain BM25 (implemented in about 40 lines, with no extra services) plus a small, auditable synonym table for player phrasing, such as "tap" → exhaust and "graveyard" → trash. A query takes about 0.05 s.

**"Never invent a rule number."** The model is told to cite only numbers that appear in the passages. The app does not trust that. `CitationChecker` resolves every `[CR …]`, `[TR …]`, `[S#]` and "rule NNN" mention against the full index:

- Verified numbers are linked to `CorePDF#page=N`.
- Numbers that don't exist are shown as `⚠ … not found` and removed from the citation list, with a warning.
- Numbers that exist but weren't among the retrieved passages get a "double-check" note.

An "answered" result with no verifiable citation is downgraded to low confidence with a warning.

---

## Prompt patterns

All model-facing text is in **`riftbound/prompts.py`**. The system prompt is assembled from named constants, one per pattern, from the course reading (White et al., *A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT*). In the app, turn on **"Show the prompts sent to the model"** in the sidebar to see the exact prompt for any question.

### 1. Persona (`PERSONA_PATTERN`)

> Act as a patient Riftbound rules explainer, like an experienced judge helping a player at a local game store. […] Provide the outputs that persona would create:
> - a direct ruling first, then a plain-language explanation a newer player can follow;
> - a step-by-step walk through the order in which things happen;
> - short definitions of any game terms you use (for example Chain, Showdown, Might, Exhaust), each tied to the rule that defines it;
> - one small, concrete example with specific numbers.

It follows the catalog's two statements: "Act as persona X" and "Provide outputs that persona X would create." **UX benefit:** players get judge-style answers with the ruling first, then terms explained, then a worked example. They don't get a dense paraphrase of a 142-page rules document. The persona also keeps the model on rules and away from strategy advice.

### 2. Question Refinement (`QUESTION_REFINEMENT_PATTERN`)

> Within the scope of Riftbound rules questions, first restate the player's question as a better, more precise rules question: name the cards, the timing (whose turn, which phase or step, whether a Chain or Showdown is open), and the locations […] Put it in "refined_question".
> Then check whether the scenario is missing a detail that would change the ruling […]
> - If such a detail is missing and the ruling would differ depending on it, do NOT guess. Set status to "needs_clarification", list the missing details, ask ONE focused question in "clarifying_question", and give 2-4 short likely answers in "clarifying_options".
> - If the missing detail would not change the ruling, answer anyway and record what you assumed in "assumptions".

It follows the catalog's "Within scope X, suggest a better version of the question" and "prompt me if I would like to use the better version." **UX benefit:** the UI shows *"How I understood your question"*, so the player can see whether the model read the situation correctly. When a decisive detail is missing, the player gets one precise question with one-click answer buttons instead of a confident wrong ruling. The app also detects card names it doesn't recognize and tells the model not to guess their text. Their answer is sent back as a "PLAYER'S ANSWER TO YOUR CLARIFYING QUESTION" section.

### 3. Visualization Generator (`VISUALIZATION_GENERATOR_PATTERN`)

> When your answer is well supported (status "answered"), generate a small structured diagram description that the app will hand to Graphviz to draw. You do not draw anything yourself. […] Optionally fill "board" with the game state of the scenario AS STATED by the player […] Only include objects the player mentioned or that your steps create. […] The diagram is an illustration of the stated scenario, not an official ruling.

It follows the catalog's "Generate an X that I can provide to tool Y to visualize it." Here X is structured zones/objects/moves/steps JSON and Y is Graphviz. The model never writes DOT. `riftbound/diagram.py` validates the data and draws it deterministically: moves to zones that weren't defined are dropped, and text is escaped. **UX benefit:** combat and movement questions get a labeled board picture and a numbered sequence of events. Because the drawing is deterministic, it can't misrepresent game state the way a generated image could. Each diagram is captioned as an illustration.

### Supporting pieces

- **Template** (`OUTPUT_TEMPLATE`): a fixed JSON template, so the UI can render every answer the same way (tabs, citations, buttons).
- **Grounding rules** (`GROUNDING_RULES`): the retrieval contract. Use only the supplied sources, follow the precedence order, cite exact numbers, keep gameplay and tournament separate, and say "not_supported" rather than guess.

---

## Tests

```bash
pytest                                   # 36 tests, no API key or network needed
python scripts/run_scenarios.py --retrieval   # scenario retrieval checks, no key needed
python scripts/run_scenarios.py               # full end-to-end run with the real LLM (needs a key)
```

- `tests/test_parsing.py`: rule-number parsing, both errata page layouts, card symbol normalization, errata precedence, legend naming.
- `tests/test_index.py`: checks against the committed index (version recorded, rule numbers exist and link to PDF pages, Elnuk Herd errata wins, card detection), plus retrieval checks for every scenario.
- `tests/test_explainer.py`: the pipeline with a stub LLM. Covers the pattern blocks in the prompt, the rules version and passages in the prompt, invented rule numbers being flagged and not linked, downgrading uncited answers, the clarification round trip, unknown cards, and diagram validation.
- `tests/test_app.py`: drives the Streamlit UI headlessly (Streamlit `AppTest`) with a stub LLM: the answer view, citations, and clarification buttons.

**Scenarios** (`scenarios/scenarios.json`). Each one lists the expected status and the rules/sources retrieval must find:

| id | What it tests | Expected |
|---|---|---|
| combat-damage-assignment | Splitting 5 damage between two 3 Might defenders (CR 467.2.c.3) | answered |
| **ambiguous-respond-to-spell** | "Can I respond with my spell?" (depends on Reaction/Action and card text) | **needs_clarification** |
| ambiguous-respond-to-spell-clarified | Same, after "My spell has [Reaction]" | answered |
| errata-elnuk-herd | Must use the 2026-10-09 errata wording, not the printed text | answered |
| scoring-twice | Once per battlefield per turn (CR 472) | answered |
| gameplay-vs-tournament-banned-card | Called Shot: legal in gameplay, banned in sanctioned Constructed | answered |
| **unsupported-2028-rotation** | Riot only says rotation is *intended* for 2028; no set list exists | **not_supported** |
| **unknown-card** | "Shadow Mirage King" is not an official card | **needs_clarification** (asks for card text) |
| hidden-timing | Hidden keyword (CR 811) | answered |
| direct-rule-lookup | "What does rule 467.2.c.4 mean?" | answered |

`run_scenarios.py` writes `scenarios/last_run.md` with each status, citations and warnings. Commit that file after a real run as evidence for the write-up.

---

## Live demo script (under 2 minutes)

1. **(0:00) Open the app.** Point at the blue banner: Core Rules last updated 2026-10-09, effective 2026-10-16, 2,494 rules indexed, errata through Radiance.
2. **(0:15) Click "Combat damage split" → Explain.** Show the refined question ("How I understood your question"), the short ruling, and the **CR 467.2.c.3** link. Click it: it opens the official PDF at page 102. Show *Step by step* and *Diagram* (board + sequence, labeled as an illustration).
3. **(0:50) Click "Respond to a spell (ambiguous)" → Explain.** The app asks one focused question (for example, whether your spell has Reaction) with answer buttons. Click one and the answer appears with citations. *That's the Question Refinement pattern.*
4. **(1:20) Click "Errata: Elnuk Herd".** Open *Cards recognized*: the current text comes from the Radiance errata, and the printed text is shown underneath.
5. **(1:35) Click "Not in sources: 2028 rotation".** The app says the official sources don't settle it, rather than inventing a list.
6. **(1:50) Toggle "Show the prompts sent to the model"** to show the Persona / Question Refinement / Visualization Generator blocks.

Before recording, run `python scripts/run_scenarios.py` once with your key to confirm every scenario behaves as expected.

---

## Project layout

```
app.py                     Streamlit UI
riftbound/
  prompts.py               ALL prompt text: Persona, Question Refinement, Visualization Generator, Template, Grounding
  knowledge.py             index loading, BM25 retrieval, card matching
  explainer.py             retrieval -> prompt -> LLM -> citation verification
  llm.py                   Gemini / Groq clients (keys from env only)
  diagram.py               deterministic Graphviz from structured output
  parsing.py               PDF/HTML/card-gallery parsers
  refresh.py               `python -m riftbound.refresh` source updater
  sources.py               Rules Hub discovery
  config.py                settings from environment / .env
data/                      committed index: manifest.json, passages.jsonl, cards.json (raw/ is gitignored)
scenarios/scenarios.json   test scenarios
scripts/run_scenarios.py   end-to-end scenario runner
tests/                     pytest suite
.env.example               template for your API key (copy to .env; never commit .env)
```

---

## Limitations

- **Card text coverage:** the app knows what Riot's Card Gallery and errata articles contain on the refresh date. Cards revealed later, promo-only cards, or names it can't match need their text pasted into the "Card text" box. Pasted text is labeled as unverified in the prompt.
- **Retrieval is keyword-based:** BM25 with a small synonym table. Unusual phrasing can miss a relevant rule. The retrieved passages are always shown, so a miss is visible. Rephrasing with official terms (Chain, Showdown, Exhaust) helps.
- **The LLM can still misread a rule.** Citations are verified mechanically, but whether the cited rule *supports* the claim is not. Each answer links to the exact passage so the player can check, and the app is not a substitute for a judge at sanctioned events.
- **Older FAQ/patch-note rulings** were written against older Core Rules versions. They are included with dates and lower precedence, and their internal rule numbers may be outdated.
- **Effective date** is taken from the newest patch-notes title ("Effective October 16, 2026"). If Riot stops including it, the manifest falls back to the Core Rules "Last updated" date and says so.
- **Parsing depends on Riot's page layouts.** If the Rules Hub, articles, or Card Gallery change format, `refresh` may fail loudly. The committed `data/` keeps the app working until the parser is updated.
- **Free API tiers** have rate limits. Each question is one call of roughly 5.5k prompt tokens plus up to 2k for the answer.
  - On Groq's free tier, `openai/gpt-oss-120b` allows 8,000 tokens per minute. One question answers in about 2-3 s, but a second question within the same minute waits for the window, about 15-30 s. Pace a live demo about a minute apart, or use a Gemini key, whose limits are much higher.
  - On a rate-limit error the app waits as long as the provider asks (up to 30 s) and retries, then switches to the other provider if both keys are set.
  - If a request is too large for one Groq model, it tries `llama-3.3-70b-versatile`.
  - `GROQ_REASONING_EFFORT=low` is the default. It gave the same rulings as medium in testing at roughly a tenth of the latency.
