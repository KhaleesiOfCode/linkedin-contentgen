import json
import random
from openai import OpenAI
from config import LLM_API_KEY, LLM_MODEL, LLM_ENDPOINT, POST_TONE, POST_LENGTH, POSTS_PER_DAY, IMAGE_GEN_ENABLED, DRAFTS_DIR
from drafts import create_draft, get_draft
from content_calendar import get_current_week, pick_topic
from image_gen import generate_image

SYSTEM_PROMPT = """You are a LinkedIn content strategist. Generate engaging, professional LinkedIn posts.

Rules:
- Write in first person with a personal/professional voice
- Use short paragraphs and line breaks for readability
- Include a hook in the first 1-2 lines
- End with a question or call-to-engagement (2-3 relevant hashtags)
- Never use emoji unless it adds genuine value
- Keep it authentic — no corporate buzzwords
- {tone}
- Target length: {length}"""


def generate_post(client: OpenAI, topic: str, week: dict) -> str:
    system = SYSTEM_PROMPT.format(tone=POST_TONE, length=POST_LENGTH)
    user_prompt = (
        f"This week's theme is \"{week['name']}\". "
        f"Write a LinkedIn post about: {topic}. "
        f"Share a personal insight, lesson learned, or contrarian take. "
        f"Make it feel like something a thoughtful data/AI professional would actually post."
    )
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=1200,
    )
    return resp.choices[0].message.content.strip()


def generate_from_custom_prompt(custom_topic: str, week_override: str | None = None) -> list[dict]:
    week = get_current_week(week_override)
    if not LLM_API_KEY:
        draft = create_draft(f"[Custom prompt — set LLM_API_KEY to generate]\n\nYour idea: {custom_topic}", custom_topic, week["name"])
        if IMAGE_GEN_ENABLED:
            img_file = generate_image(draft["id"], custom_topic, week["name"], draft["content"])
            if img_file:
                draft["image_file"] = img_file
                (DRAFTS_DIR / f"{draft['id']}.json").write_text(json.dumps(draft, indent=2))
        return [draft]

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_ENDPOINT)
    try:
        content = generate_post(client, custom_topic, week)
    except Exception as e:
        content = f"[Generation failed: {e}]\n\nTried to write about: {custom_topic}"

    draft = create_draft(content, custom_topic, week["name"])
    if IMAGE_GEN_ENABLED:
        img_file = generate_image(draft["id"], custom_topic, week["name"], content)
        if img_file:
            draft["image_file"] = img_file
            (DRAFTS_DIR / f"{draft['id']}.json").write_text(json.dumps(draft, indent=2))
    return [draft]


def generate_daily_drafts(count: int | None = None) -> list[dict]:
    count = count or POSTS_PER_DAY
    week = get_current_week()

    if not LLM_API_KEY:
        return _generate_fallback_drafts(count, week)

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_ENDPOINT)
    used = []
    drafts = []

    for _ in range(count):
        topic = pick_topic(week, exclude=used)
        used.append(topic)
        try:
            content = generate_post(client, topic, week)
        except Exception as e:
            content = f"[Generation failed: {e}]\n\nLet's talk about {topic}..."
        draft = create_draft(content, topic, week["name"])
        if IMAGE_GEN_ENABLED:
            img_file = generate_image(draft["id"], topic, week["name"], content)
            if img_file:
                draft["image_file"] = img_file
                (DRAFTS_DIR / f"{draft['id']}.json").write_text(json.dumps(draft, indent=2))
        drafts.append(draft)

    return drafts


def _generate_fallback_drafts(count: int, week: dict) -> list[dict]:
    fallback_pool = {
        "LLMs & Models": [
            "I spent last weekend benchmarking Claude 4, GPT-4o, and Gemini 2.5 Pro on the same real-world coding task: building a REST API with authentication, rate limiting, and a PostgreSQL backend.\n\n"
            "Here's what I found:\n\n"
            "Claude 4 was the strongest on architecture — it suggested a clean layered design with middleware for auth, repository pattern for data access, and proper error handling out of the box. However, it introduced a subtle bug in the token refresh logic that took me 20 minutes to catch.\n\n"
            "GPT-4o was the fastest by a significant margin — first working solution in under 90 seconds. But it cut corners: no input validation, hardcoded config values, and minimal error handling. Great for rapid prototyping, risky for production.\n\n"
            "Gemini 2.5 Pro was the most thorough — it generated extensive comments, handled every edge case I could think of, and even suggested a migration strategy from SQLite to Postgres. The tradeoff was verbosity: the response was nearly 3x longer than GPT-4o's.\n\n"
            "The real takeaway? There's no single \"best\" model. The winner depends entirely on what you're optimizing for:\n"
            "- Speed of iteration: GPT-4o\n"
            "- Architecture quality: Claude 4\n"
            "- Exhaustiveness: Gemini 2.5 Pro\n\n"
            "I've started using a two-pass approach: GPT-4o for the first draft, Claude 4 for the architecture review. It's been working well.\n\n"
            "What's your current model strategy? Have you found a combination that works?\n\n"
            "#LLM #AIComparison #Coding",
            "Context windows just hit 1 million tokens across multiple models. On paper, that means you can feed an entire codebase into a single prompt. In practice, it's not that simple.\n\n"
            "I've been experimenting with 100K+ token contexts for the last month, and here's what I've learned:\n\n"
            "First, retrieval quality matters far more than context size. I ran a controlled test: 50 questions answered using (a) a 200K context window with no retrieval, vs (b) a 16K context window with a hybrid search pipeline. Result: the smaller context with good retrieval was 34% more accurate.\n\n"
            "The reason is what researchers call the \"lost in the middle\" problem — models consistently perform worse on information in the middle of long contexts. The first 10% and last 10% of tokens get the most attention. Everything else fades.\n\n"
            "Where large context windows genuinely shine:\n"
            "1. Analyzing entire codebases for security vulnerabilities\n"
            "2. Cross-referencing multiple long documents (legal, research papers)\n"
            "3. Long-running conversations where you need full history\n\n"
            "For everything else — documentation Q&A, customer support, content generation — invest in your chunking strategy first. Paragraph-level chunks with overlap, hybrid search (BM25 + embeddings), and reranking will outperform a bigger context window every time.\n\n"
            "What's been your experience with long contexts? Love them or still relying on RAG?\n\n"
            "#RAG #LLM #InformationRetrieval",
        ],
        "AI Tools & Dev": [
            "I've been using Claude Code daily for three weeks now. Here's an honest breakdown of what it's actually good at and where it still falls short.\n\n"
            "The workflow is deceptively simple: you describe what you want in natural language, Claude plans the approach, writes the code, and presents a diff for you to review. You can iterate by giving follow-up instructions. It's like pair programming with a tireless junior who reads documentation faster than any human.\n\n"
            "Where it excels:\n"
            "- Refactoring legacy code: I pointed it at a 5-year-old Python service with no tests and asked it to add type hints, break 500-line functions into smaller units, and add unit tests. It handled 80% of the work in one pass.\n"
            "- Writing boilerplate: API clients, data models, migration scripts — the tedious stuff that takes hours gets done in minutes.\n"
            "- Explaining unfamiliar code: I dropped in a codebase I'd never seen before and asked for a high-level architecture diagram in text. The summary was accurate enough that I could start contributing within an hour.\n\n"
            "Where it struggles:\n"
            "- Novel problems: if there aren't examples in its training data, the quality drops noticeably. It sometimes invents APIs that don't exist.\n"
            "- Cross-file refactoring: it occasionally misses updating all references when renaming a function across multiple files.\n"
            "- Security context: it doesn't always flag insecure patterns unless explicitly told to check.\n\n"
            "My verdict: Claude Code won't replace experienced engineers, but it's the best tool I've found for amplifying productivity. The key is treating it as a collaborator, not an oracle — review everything, but let it handle the grunt work.\n\n"
            "Have you tried Claude Code or similar AI coding agents? What's your workflow look like?\n\n"
            "#ClaudeCode #AIDevelopment #Productivity",
            "MCP — Model Context Protocol — is the most underhyped AI infrastructure development this year, and here's why it matters.\n\n"
            "Think of MCP as a universal connector for AI models, similar to what USB-C did for peripherals. Instead of building custom integrations for every data source your LLM needs to access, MCP provides a standardized protocol. One server, one client, any data source.\n\n"
            "Here's the concrete setup I've been running for two weeks:\n"
            "- An MCP server connected to my production PostgreSQL database (read-only, with row-level security)\n"
            "- Another MCP server hooked into our Jira and Confluence\n"
            "- A third connected to our GitHub repository\n\n"
            "The result? I can ask Claude questions like \"Show me all open P0 bugs assigned to our team that were filed this sprint, along with the related pull requests and any relevant design docs.\" Claude queries all three sources, correlates the data, and gives me a coherent answer in seconds.\n\n"
            "Before MCP, this would have required:\n"
            "- A custom Slack bot\n"
            "- Multiple API integrations maintained separately\n"
            "- A middleware layer to handle authentication across services\n\n"
            "The MCP specification handles discovery, authentication, and transport. You write a simple server script (I used Python, but there are TypeScript examples too) that exposes the tools your model needs.\n\n"
            "If you're building AI features that need to interact with your existing infrastructure, spend a weekend prototyping with MCP. It's early but already production-usable for read-only workflows.\n\n"
            "Have you tried MCP yet? What data sources would you connect first?\n\n"
            "#MCP #AITools #Infrastructure",
        ],
        "Building with AI": [
            "I've built and shipped three RAG systems to production this year. Here's a detailed breakdown of what actually matters — beyond the tutorials.\n\n"
            "**Chunking strategy is the single biggest lever.**\n"
            "Fixed-token chunking (512 tokens, no overlap) is the default in most frameworks, and it's almost always wrong. I ran an A/B test comparing fixed-token chunks against paragraph-aware semantic chunks. The semantic approach improved retrieval accuracy by 28% on our test set.\n\n"
            "What works: split on natural boundaries (paragraphs, sections, markdown headers) with 1-2 sentences of overlap. Store the chunk along with its parent section title and document metadata. This lets you return richer context to the LLM.\n\n"
            "**Hybrid search beats pure embeddings by 15-20%.**\n"
            "We compared three retrieval strategies on a corpus of 10,000 technical documents:\n"
            "- Pure embedding similarity (text-embedding-3-large): 0.72 recall@10\n"
            "- Pure BM25 keyword search: 0.68 recall@10\n"
            "- Hybrid (BM25 + embeddings with weighted fusion): 0.84 recall@10\n\n"
            "The hybrid approach catches queries where keyword overlap matters (product names, error codes) while still handling semantic matches. We used a simple 0.3/0.7 weight split favoring embeddings, but this should be tuned on your own data.\n\n"
            "**Evaluation is non-negotiable.**\n"
            "Before shipping our first RAG system, we built a test set of 100 query-answer pairs covering the key use cases. Each week, we added 10-20 new edge cases found in production logs. This test set caught two regressions that would have gone unnoticed until users complained.\n\n"
            "The eval doesn't need to be sophisticated — even a structured CSV with expected answer patterns catches more than you'd think. Run it before every deployment.\n\n"
            "What's been the hardest lesson from your RAG projects?\n\n"
            "#RAG #LLM #AIEngineering",
            "After shipping three LLM-powered features to production, the most important lesson wasn't about accuracy, latency, or cost — it was about reliability.\n\n"
            "Here's the problem: LLMs are non-deterministic by nature. The same prompt can produce different answers on different calls. For a chatbot, this is annoying. For a system that generates structured data for downstream processing, it's a crisis.\n\n"
            "We learned this the hard way when a customer-facing summary feature started producing JSON with varying field names. One call returned \"customer_name\", another returned \"name\", a third returned \"fullName\". Our downstream parser broke silently for 12 hours before anyone noticed.\n\n"
            "**Three things that fixed our reliability:**\n\n"
            "1. Structured outputs with Pydantic/JSON mode\n"
            "Instead of asking the LLM to \"return JSON\" in the prompt, we switched to OpenAI's structured output mode and Anthropic's tool calling. This forces the model to conform to a schema. Field names are now consistent across 99.7% of calls.\n\n"
            "2. Input validation at every layer\n"
            "We added validation at three points: before the LLM call (is the user input safe?), after the LLM call (does the output match the schema?), and before the output is used downstream (are the values within expected ranges?).\n\n"
            "3. Monitoring for drift\n"
            "We track three metrics per deployment: schema compliance rate, response time percentile distribution, and content quality score (via a smaller LLM evaluating the larger one). Alerts fire if any metric moves beyond 2 standard deviations from the baseline.\n\n"
            "The result? Our schema compliance went from 92% to 99.7%. PagerDuty alerts dropped by 80%.\n\n"
            "Invest in making your AI boring. Predictable, consistent, reliable. Users will forgive a slightly wrong answer far more quickly than an inconsistent one.\n\n"
            "What reliability patterns have you found essential for production AI?\n\n"
            "#MLOps #AIEngineering #Reliability",
        ],
        "Learn AI": [
            "A few months ago, I mentored a colleague transitioning from data analytics into AI engineering. We designed a 10-week roadmap together, and I've refined it based on what actually worked. Here's the updated version.\n\n"
            "**Weeks 1-2: Understand the transformer architecture**\n"
            "Don't just use APIs — understand what's happening under the hood. Start with 3Blue1Brown's neural network series (45 minutes total, utterly clear). Then read the \"Attention is All You Need\" paper — but use the annotated version from Jay Alammar's blog. The paper is dense; the annotations make it accessible.\n"
            "By week 2, you should be able to explain: what attention computes, why positional encoding matters, and how the encoder-decoder structure works.\n\n"
            "**Weeks 3-4: Build a RAG system from scratch**\n"
            "Not with LangChain's high-level abstractions — with raw Python, an embedding model, and a vector store. This forces you to understand chunking, embedding, retrieval, and prompt construction as separate concerns.\n"
            "Once it works, rebuild it with LangChain or LlamaIndex. The difference in effort will make you appreciate what these frameworks handle.\n\n"
            "**Weeks 5-6: Master prompt engineering systematically**\n"
            "This isn't just \"write better prompts.\" Study the research: chain-of-thought, few-shot, tree-of-thought, structured outputs. Build a test harness where you can evaluate different prompt strategies against a fixed set of queries. Measure accuracy, latency, and token cost.\n"
            "The goal: by week 6, you should be able to pick the right prompting strategy for a given task and justify why.\n\n"
            "**Weeks 7-8: Build an agent that uses tools**\n"
            "Give an LLM access to a calculator, a search engine, and a database. Start with the ReAct pattern (reasoning + acting). Then add memory and error recovery.\n"
            "The turning point is when your agent handles an unexpected error gracefully instead of crashing.\n\n"
            "**Weeks 9-10: Evaluation and observability**\n"
            "Learn how to eval LLM outputs systematically. Set up tracing with Langfuse or similar. Understand metrics: faithfulness, relevance, precision, recall. Build a regression test suite for your prompts.\n\n"
            "The most important lesson from this roadmap? You learn 10x more from building one bad project than from reading ten good tutorials. Start messy. Iterate.\n\n"
            "What's on your AI learning roadmap? Would you change anything about this approach?\n\n"
            "#LearnAI #AI #CareerGrowth",
            "My first LLM project was a chatbot that responded exclusively in Shakespearean English. \"Thou art a scallywag\" was a legitimate error message. It was ridiculous, impractical, and completely useless.\n\n"
            "And it taught me more about LLMs than a month of tutorials.\n\n"
            "Here's what building that silly project forced me to learn:\n\n"
            "**Tokenization**: I kept hitting context limits because Shakespearean English is verbose. \"Would thou kindly\" instead of \"please\" — every token counts. This taught me about token budgets and why prompt compression matters.\n\n"
            "**Temperature and sampling**: At temperature 0, the chatbot was boringly consistent. At temperature 1.5, it was creative but occasionally incoherent. I had to understand the tradeoff between creativity and reliability to find the sweet spot (0.7 for my use case).\n\n"
            "**System prompts**: Getting the chatbot to stay in character while still being helpful was harder than expected. I went through 15 iterations of the system prompt before finding one that balanced personality with utility. This taught me more about prompt engineering than any guide.\n\n"
            "**Fallback handling**: When the model couldn't understand a query, it would sometimes break character and apologize in modern English. I had to add guardrails — few-shot examples of how to handle unknown queries while staying in character.\n\n"
            "**Evaluation**: How do you test that a Shakespearean chatbot is working correctly? I built a small eval set with expected response patterns and ran it after every prompt change.\n\n"
            "The project took a weekend. Six months later, I was building production RAG systems — and every architectural decision traced back to lessons from that silly Shakespeare bot.\n\n"
            "Pick a bad idea. Build it. You'll learn more than any course will teach you.\n\n"
            "What's the weirdest project you've built that turned out to be unexpectedly educational?\n\n"
            "#AI #LearningByBuilding #100DaysOfAI",
        ],
    }
    pool = fallback_pool.get(week["name"], fallback_pool["LLMs & Models"])
    topics = [t.split("\n\n")[0].split(". ")[0][:80] + ("..." if len(t.split("\n\n")[0]) > 80 else "") for t in pool]
    drafts = []
    for i in range(min(count, len(pool))):
        draft = create_draft(pool[i], topics[i], week["name"])
        if IMAGE_GEN_ENABLED:
            img_file = generate_image(draft["id"], topics[i], week["name"], pool[i])
            if img_file:
                draft["image_file"] = img_file
                (DRAFTS_DIR / f"{draft['id']}.json").write_text(json.dumps(draft, indent=2))
        drafts.append(draft)
    return drafts


if __name__ == "__main__":
    week = get_current_week()
    drafts = generate_daily_drafts()
    print(f"Week theme: {week['name']}")
    print(f"Generated {len(drafts)} draft(s):")
    for d in drafts:
        print(f"  [{d['id']}] {d['topic']}")
