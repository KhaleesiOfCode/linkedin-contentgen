# LinkedIn Content Generator

Automated daily LinkedIn post generation with AI-powered content, themed image visuals, and a web UI for review and approval.

## How It Works

```
[Calendar] → [Topic Picker] → [DeepSeek API] → [Post + Image] → [Web UI] → [You Approve]
```

- A **4-week content calendar** rotates themes (LLMs, AI Tools, Building with AI, Learn AI)
- **DeepSeek API** generates detailed, educational posts (500+ words each)
- **Pillow-based image renderer** creates themed PNG visuals with layout detection
- **Flask web UI** lets you review, approve, reject, or regenerate posts
- **Custom prompt input** to write about your own topic

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API key
cp .env.example .env
# Edit .env with your DeepSeek or OpenAI key

# 3. Generate a post
python run.py

# 4. Open the web UI
python app.py
# → http://localhost:5000
```

## Usage

### Generate from your own idea
Open the web UI, type any topic into the **custom prompt** field, and hit "Generate from Prompt". Great for reacting to news or writing about something specific.

### Auto-generate from weekly topics
Each week follows a theme. Click "Auto-generate from weekly topics" to pick a random topic from the current week.

```bash
# Force a specific week theme
python run.py --theme "LLMs & Models"
python run.py --theme "Learn AI" --count 3
```

### Review and approve
The dashboard shows all drafts. You can:
- **View** — full post content with generated image
- **Approve** — marks as ready to post
- **Reject** — discards the draft
- **Reopen** — moves back to pending
- **Download Image** — saves the PNG for manual LinkedIn posting

## Content Calendar

| Week | Theme | Sample Topics |
|------|-------|---------------|
| 1 | LLMs & Models | GPT-4o vs Claude, reasoning models, context windows, distillation |
| 2 | AI Tools & Dev | Claude Code, MCP, Cursor vs Copilot, prompt engineering |
| 3 | Building with AI | RAG in production, eval-driven dev, structured outputs, agents |
| 4 | Learn AI | Learning roadmap, projects, papers, staying current |

## Image Layouts

The image generator detects content structure and picks a layout automatically:

| Layout | Detected When | Shows |
|--------|---------------|-------|
| **Comparison** | Models/tools compared (Claude vs GPT) | Side-by-side columns with attributes |
| **Steps** | Numbered steps or "Week X" patterns | Vertical numbered timeline |
| **Bullets** | Bullet-point lists | Card with dot-point takeaways |
| **Default** | Everything else | Centered quote with insight |

## Configuration

Edit `.env`:

```env
# DeepSeek
LLM_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
LLM_ENDPOINT=https://api.deepseek.com/v1

# OpenAI (for DALL-E image gen)
# LLM_API_KEY=sk-your-openai-key
# LLM_MODEL=gpt-4o
# LLM_ENDPOINT=https://api.openai.com/v1

POST_TONE="professional but conversational, occasional humour"
POST_LENGTH="400-600 words"
POSTS_PER_DAY=1
```

Without an API key, the system uses built-in fallback content (still detailed and themed).

## Project Structure

```
├── app.py              # Flask web UI
├── generator.py        # AI post generation
├── image_gen.py        # PNG image renderer (Pillow)
├── content_calendar.py # Weekly theme rotation
├── prompts.py          # Daily writing prompts
├── drafts.py           # JSON draft storage
├── scheduler.py        # Daily auto-generation
├── config.py           # Environment configuration
├── templates/          # Flask HTML templates
├── static/style.css    # UI styles
└── drafts/             # Generated drafts + images
```
