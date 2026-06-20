"""Daily writing prompts for when you want to write your own post."""

import random
from content_calendar import get_current_week

PROMPT_POOL = {
    "LLMs & Models": [
        "What's one myth about LLMs you wish more people understood?",
        "Describe a recent experience where a model surprised you — good or bad.",
        "If you could ask any AI researcher one question, what would it be?",
        "Open-source vs closed-source LLMs — where do you stand and why?",
        "What's the most underrated LLM feature most people don't use?",
        "How do you evaluate whether a model is right for your use case?",
        "Share a tip that improved your LLM prompt quality significantly.",
        "What will LLMs be able to do a year from now that they can't today?",
    ],
    "AI Tools & Dev": [
        "Which AI coding tool has changed your workflow the most? How?",
        "What's a task you refuse to delegate to AI — and why?",
        "Describe your ideal AI-assisted development workflow.",
        "Have you tried Claude Code, Cursor, or Copilot? What's your verdict?",
        "What's something AI code assistants still get consistently wrong?",
        "How do you prompt-engineer for code vs for text? Different approaches?",
        "What non-coding task have you successfully automated with AI?",
        "MCP, function calling, plugins — which integration pattern wins?",
    ],
    "Building with AI": [
        "What's the hardest lesson you learned building an AI-powered product?",
        "RAG vs fine-tuning — which one have you found more useful in practice?",
        "How do you handle hallucination in production systems?",
        "What's your evaluation strategy for LLM outputs?",
        "Share a debugging story from an AI project that taught you something.",
        "What infrastructure do you wish existed for AI applications?",
        "How do you balance cost vs quality when calling LLM APIs?",
        "What's a non-obvious edge case you've encountered with AI in production?",
    ],
    "Learn AI": [
        "What's the one resource that made AI 'click' for you?",
        "If you were starting from zero today, how would you learn AI?",
        "What project would you recommend for someone learning LLMs?",
        "What's a concept in AI that took you embarrassingly long to understand?",
        "How do you stay updated without getting overwhelmed by AI news?",
        "What skill from data engineering transfers best to AI engineering?",
        "Books, papers, or blogs — which format teaches you best?",
        "What's your unpopular opinion about how AI should be taught?",
    ],
}


def get_daily_prompt(week_override: str | None = None) -> dict:
    week = get_current_week(week_override)
    pool = PROMPT_POOL.get(week["name"], PROMPT_POOL["LLMs & Models"])
    prompt = random.choice(pool)
    return {
        "theme": week["name"],
        "prompt": prompt,
        "emoji": week["emoji"],
    }
