import os
from datetime import date, datetime
import random

WEEKS = [
    {
        "name": "LLMs & Models",
        "emoji": "LLM",
        "topics": [
            "GPT-4o vs Claude 4 vs Gemini — how the models compare today",
            "Open source LLMs (Llama, Mistral, DeepSeek) — when to use them",
            "How reasoning models (o3, Claude thinking) change what's possible",
            "Context windows are growing — what 1M+ tokens unlocks",
            "Multimodal LLMs: text + image + code in one model",
            "Model distillation — smaller, faster, cheaper for production",
            "The cost of LLM inference and how to optimize it",
            "Latency vs quality tradeoffs when choosing a model",
            "Fine-tuning vs RAG vs prompting — which one when",
            "Synthetic data generation using LLMs",
        ],
    },
    {
        "name": "AI Tools & Dev",
        "emoji": "TOOL",
        "topics": [
            "Claude Code — coding with AI agents in the terminal",
            "Cursor vs Copilot vs Claude Code — which AI coding tool wins",
            "AI code review — what it catches and what it misses",
            "Prompt engineering for developers — patterns that work",
            "Building AI agents that use tools and APIs",
            "MCP (Model Context Protocol) — connecting LLMs to your data",
            "OpenAI Codex CLI and the future of AI-assisted development",
            "Using LLMs to generate tests, docs, and migrations",
            "AI-powered debugging — how to use LLMs to fix bugs faster",
            "Version control for prompts — treating prompts like code",
        ],
    },
    {
        "name": "Building with AI",
        "emoji": "BUILD",
        "topics": [
            "RAG from scratch — what I learned building a production system",
            "Evaluation-driven development for LLM applications",
            "Structured outputs from LLMs — JSON mode, tool calling",
            "Caching strategies for LLM API calls to reduce cost",
            "Guardrails and input validation for LLM apps",
            "A/B testing LLM prompts in production",
            "Observability for AI apps — tracing, logging, monitoring",
            "Vector databases compared: Pinecone vs Weaviate vs pgvector",
            "Building a coding assistant — lessons from the trenches",
            "Data pipelines for RAG — cleaning chunking embedding",
        ],
    },
    {
        "name": "Learn AI",
        "emoji": "LEARN",
        "topics": [
            "How to learn LLMs in 2025 — a roadmap from zero to production",
            "The math you actually need for working with AI",
            "Best resources to understand transformer architectures",
            "Building your first RAG system — a weekend project guide",
            "How I stay current with AI without burning out",
            "From data engineer to AI engineer — skills to bridge the gap",
            "Books, papers, and courses that actually taught me something",
            "Learning by building — project ideas to level up your AI skills",
            "Understanding attention is all you need — explained simply",
            "Communities and newsletters worth following for AI",
        ],
    },
]

WEEK_OFFSETS = {w["name"]: i for i, w in enumerate(WEEKS)}


def get_current_week(override: str | None = None) -> dict:
    name = override or os.getenv("OVERRIDE_THEME", "")
    if name:
        for w in WEEKS:
            if w["name"].lower() == name.lower():
                return w
    reference = date(2025, 1, 6)
    weeks_elapsed = (date.today() - reference).days // 7
    return WEEKS[weeks_elapsed % len(WEEKS)]


def get_week_for(date_str: str) -> dict:
    d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    reference = date(2025, 1, 6)
    weeks_elapsed = (d - reference).days // 7
    return WEEKS[weeks_elapsed % len(WEEKS)]


def pick_topic(week: dict, exclude: list[str] | None = None) -> str:
    candidates = [t for t in week["topics"] if t not in (exclude or [])]
    return random.choice(candidates)


def get_upcoming_weeks(count: int = 4) -> list[dict]:
    reference = date(2025, 1, 6)
    weeks_elapsed = (date.today() - reference).days // 7
    result = []
    for i in range(count):
        idx = (weeks_elapsed + i) % len(WEEKS)
        w = dict(WEEKS[idx])
        w["week_num"] = i + 1
        result.append(w)
    return result
