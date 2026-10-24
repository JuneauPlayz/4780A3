"""Paths and environment-driven settings. API keys are only ever read from the environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # downloaded originals (gitignored)
MANIFEST_PATH = DATA_DIR / "manifest.json"
PASSAGES_PATH = DATA_DIR / "passages.jsonl"
CARDS_PATH = DATA_DIR / "cards.json"

load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# "auto" picks Gemini if GEMINI_API_KEY is set, otherwise Groq if GROQ_API_KEY is set.
LLM_PROVIDER = env("LLM_PROVIDER", "auto").lower()
GEMINI_MODEL = env("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = env("GROQ_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(env("LLM_TEMPERATURE", "0.2"))
# Groq free tier allows 8,000 tokens per minute for gpt-oss-120b, counting prompt + max completion.
GROQ_MAX_TOKENS = int(env("GROQ_MAX_TOKENS", "2000"))
GROQ_REASONING_EFFORT = env("GROQ_REASONING_EFFORT", "low")

# Retrieval sizes: how many passages of each kind go into the prompt.
TOP_K_CORE = int(env("TOP_K_CORE", "6"))
TOP_K_OTHER = int(env("TOP_K_OTHER", "3"))
# Long passages are cut to this many characters in the prompt (the full text stays linked).
PROMPT_PASSAGE_CHARS = int(env("PROMPT_PASSAGE_CHARS", "2400"))
