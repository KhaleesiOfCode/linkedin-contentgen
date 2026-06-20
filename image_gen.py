import base64
import textwrap
import re
from pathlib import Path
from io import BytesIO
from openai import OpenAI
from config import LLM_API_KEY, IMAGE_MODEL, IMAGE_SIZE, IMAGES_DIR

THEME_COLORS = {
    "LLMs & Models": ((26, 26, 46), (22, 33, 62), (15, 52, 96)),
    "AI Tools & Dev": ((13, 27, 42), (27, 40, 56), (65, 90, 119)),
    "Building with AI": ((26, 26, 46), (83, 52, 131), (233, 69, 96)),
    "Learn AI": ((44, 62, 80), (52, 73, 94), (127, 140, 141)),
}

W = 1024
H = 1024


def _image_path(draft_id: str) -> Path:
    return IMAGES_DIR / f"{draft_id}.png"


def _svg_path(draft_id: str) -> Path:
    return IMAGES_DIR / f"{draft_id}.svg"


def image_exists(draft_id: str) -> bool:
    return _image_path(draft_id).exists() or _svg_path(draft_id).exists()


def get_image_file(draft_id: str) -> str | None:
    png = _image_path(draft_id)
    if png.exists():
        return png.name
    svg = _svg_path(draft_id)
    if svg.exists():
        return svg.name
    return None


def delete_image(draft_id: str) -> None:
    for path in (_image_path(draft_id), _svg_path(draft_id)):
        if path.exists():
            path.unlink()


def _make_prompt(topic: str, week_theme: str) -> str:
    return (
        f"A professional LinkedIn post header image about {topic}. "
        f"Theme: {week_theme}. Minimalist tech composition, "
        f"muted blues and greys, abstract data or AI visuals, "
        f"no text, no people. Clean, modern, suitable for a social media banner."
    )


def generate_image(draft_id: str, topic: str, week_theme: str, content: str = "") -> str | None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    if not LLM_API_KEY:
        return _render_png(draft_id, topic, week_theme, content)

    prompt = _make_prompt(topic, week_theme)
    client = OpenAI(api_key=LLM_API_KEY)

    try:
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=IMAGE_SIZE,
            quality="standard",
            n=1,
            response_format="b64_json",
        )
        img_data = base64.b64decode(resp.data[0].b64_json)
        dest = _image_path(draft_id)
        dest.write_bytes(img_data)
        return dest.name
    except Exception as e:
        print(f"  [DALL-E failed: {e}, rendering locally]")
        return _render_png(draft_id, topic, week_theme, content)


def _detect_layout(content: str) -> str:
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    text = " ".join(lines)
    model_names = ["Claude", "GPT-4", "Gemini", "DeepSeek", "Llama", "Mistral"]
    model_count = sum(1 for m in model_names if m.lower() in text.lower())
    has_vs = bool(re.search(r'\b(vs|versus)\b', text.lower()))
    has_steps = any(p.lower() in text.lower() for p in ["Week", "Step", "Phase"])
    numbered_items = len([l for l in lines if re.match(r'^\d+[\.\)]', l)])
    bullet_items = len([l for l in lines if l.startswith(("- ", "* ", "→"))])

    if (model_count >= 2 or has_vs) and numbered_items <= 2:
        return "comparison"
    if has_steps or numbered_items >= 3:
        return "steps"
    if bullet_items >= 2:
        return "bullets"
    return "default"


def _render_png(draft_id: str, topic: str, week_theme: str, content: str) -> str | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    c1, c2, c3 = THEME_COLORS.get(week_theme, ((26, 26, 46), (22, 33, 62), (15, 52, 96)))

    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    _draw_gradient(draw, c1, c3)

    layout = _detect_layout(content) if content else "default"

    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 36)
        font_reg = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_serif = ImageFont.truetype("timesbd.ttf", 30)
    except (IOError, OSError):
        font_bold = font_reg = font_small = font_title = font_serif = ImageFont.load_default()

    _draw_decorative_circles(draw, c2)
    _draw_theme_label(draw, week_theme, font_small)

    lines_clean = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")] if content else []

    if layout == "comparison":
        _layout_comparison_pil(draw, topic, lines_clean, font_title, font_reg, font_small)
    elif layout == "steps":
        _layout_steps_pil(draw, topic, lines_clean, font_title, font_reg, font_small)
    elif layout == "bullets":
        _layout_bullets_pil(draw, topic, lines_clean, font_title, font_reg, font_small, font_serif)
    else:
        _layout_default_pil(draw, topic, lines_clean, font_title, font_reg, font_small, font_serif)

    _draw_footer(draw, font_small)

    dest = _image_path(draft_id)
    img.save(dest, "PNG")
    return dest.name


def _draw_gradient(draw, c1, c3):
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c3[0] - c1[0]) * t)
        g = int(c1[1] + (c3[1] - c1[1]) * t)
        b = int(c1[2] + (c3[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))


def _draw_decorative_circles(draw, c2):
    for cx, cy, r, a in [(880, 150, 280, 50), (150, 880, 350, 38)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*c2, a), outline=None)


def _draw_theme_label(draw, theme, font):
    tw = draw.textlength(theme.upper(), font=font)
    draw.text(((W - tw) // 2, 30), theme.upper(), fill=(255, 255, 255, 100), font=font)


def _draw_footer(draw, font):
    draw.rectangle([(0, H - 54), (W, H)], fill=(0, 0, 0, 50))
    tw = draw.textlength("linkedin.com/in/yourprofile", font=font)
    draw.text(((W - tw) // 2, H - 40), "linkedin.com/in/yourprofile", fill=(255, 255, 255, 80), font=font)


def _wrapped_lines(text, font, max_w, draw):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines if lines else [text[:60]]


def _extract_bullets_pil(lines):
    bullets = []
    for l in lines:
        if l.startswith(("- ", "* ", "→", "•")):
            bullets.append(l.lstrip("-*→• ").strip())
            if len(bullets) >= 5:
                break
    return bullets


def _find_question(lines):
    for l in lines:
        if "?" in l:
            return l[:120]
    return ""


def _find_insight(lines):
    for l in lines:
        if any(k in l.lower() for k in ["takeaway", "lesson", "the key", "remember", "my verdict"]):
            return l[:130]
    return ""


def _layout_comparison_pil(draw, topic, lines, font_title, font_reg, font_small):
    tw = draw.textlength(topic[:70], font=font_title)
    draw.text(((W - tw) // 2, 110), topic[:70], fill=(255, 255, 255, 255), font=font_title)

    items = []
    for l in lines:
        for name in ["Claude", "GPT-4", "Gemini", "DeepSeek", "Llama", "Mistral"]:
            if name.lower() in l.lower():
                items.append((name, l[:130]))
                break

    if not items:
        items = [("Approach A", "Strengths and tradeoffs"), ("Approach B", "Alternative benefits")]

    cols = min(len(items), 4)
    col_w = 800 // cols
    start_x = (W - (col_w * cols)) // 2
    card_y = 200
    card_h = 250

    for i, (label, detail) in enumerate(items[:4]):
        cx = start_x + i * col_w
        draw.rounded_rectangle([cx + 8, card_y, cx + col_w - 8, card_y + card_h], radius=10,
                               fill=(*((255, 255, 255) if i == 0 else (255, 255, 255)), 15),
                               outline=(*((255, 255, 255) if i == 0 else (255, 255, 255)), 30), width=1)
        lw = draw.textlength(label, font=font_title)
        draw.text((cx + (col_w - lw) // 2, card_y + 30), label, fill=(255, 255, 255, 255), font=font_title)
        dl = _wrapped_lines(detail, font_small, col_w - 40, draw)
        y = card_y + 75
        for line in dl[:5]:
            lw = draw.textlength(line, font=font_small)
            draw.text((cx + (col_w - lw) // 2, y), line, fill=(255, 255, 255, 190), font=font_small)
            y += 24


def _layout_steps_pil(draw, topic, lines, font_title, font_reg, font_small):
    tw = draw.textlength(topic[:70], font=font_title)
    draw.text(((W - tw) // 2, 110), topic[:70], fill=(255, 255, 255, 255), font=font_title)

    steps = []
    for l in lines:
        if re.match(r'^(Week|Step|Phase)\s*\d', l) or re.match(r'^\d+[\.\)]', l):
            steps.append(l[:80])
            if len(steps) >= 5:
                break
    if not steps:
        steps = ["Step 1: Get started", "Step 2: Learn the basics", "Step 3: Build something"]

    start_y = 200
    step_h = 95
    dot_r = 18

    for i, step in enumerate(steps[:5]):
        cy = start_y + i * step_h
        draw.ellipse([160 - dot_r, cy - dot_r + 20, 160 + dot_r, cy + dot_r + 20],
                     fill=(255, 255, 255, 35), outline=(255, 255, 255, 70), width=2)
        tw2 = draw.textlength(str(i + 1), font=font_title)
        draw.text((160 - tw2 // 2, cy - 12 + 20), str(i + 1), fill=(255, 255, 255, 255), font=font_title)
        draw.text((200, cy + 6 + 20), step, fill=(255, 255, 255, 255), font=font_reg)

        if i < len(steps) - 1:
            draw.line([(160, cy + 20 + dot_r + 2), (160, cy + step_h)], fill=(255, 255, 255, 35), width=2)


def _layout_bullets_pil(draw, topic, lines, font_title, font_reg, font_small, font_serif):
    tw = draw.textlength(topic[:70], font=font_title)
    draw.text(((W - tw) // 2, 110), topic[:70], fill=(255, 255, 255, 255), font=font_title)

    bullets = _extract_bullets_pil(lines)
    if not bullets:
        bullets = ["Key insight from this article"] * 3

    card_x, card_y, card_w, card_h = 80, 200, W - 160, 520
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16,
                           fill=(255, 255, 255, 12), outline=(255, 255, 255, 25), width=1)

    label = "KEY TAKEAWAYS"
    lw = draw.textlength(label, font=font_reg)
    draw.text(((W - lw) // 2, card_y + 30), label, fill=(255, 255, 255, 120), font=font_reg)

    y = card_y + 80
    for i, b in enumerate(bullets):
        draw.ellipse([110, y - 4, 120, y + 6], fill=(233, 69, 96, 200))
        bl = _wrapped_lines(b, font_small, card_w - 100, draw)
        for line in bl:
            draw.text((135, y - 10), line, fill=(255, 255, 255, 215), font=font_small)
            y += 28
        y += 10

    q = _find_question(lines)
    if q:
        ql = _wrapped_lines(q, font_small, card_w - 40, draw)
        y2 = card_y + card_h - len(ql) * 24 - 30
        for line in ql:
            lw = draw.textlength(line, font=font_small)
            draw.text(((W - lw) // 2, y2), line, fill=(255, 255, 255, 120), font=font_small)
            y2 += 24


def _layout_default_pil(draw, topic, lines, font_title, font_reg, font_small, font_serif):
    tw = draw.textlength(topic[:70], font=font_title)
    draw.text(((W - tw) // 2, 110), topic[:70], fill=(255, 255, 255, 255), font=font_title)

    hook = lines[0] if lines else topic
    max_w = W - 160
    hook_lines = _wrapped_lines(hook, font_serif, max_w, draw)

    card_x, card_y, card_w, card_h = 60, 200, W - 120, 320
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16,
                           fill=(255, 255, 255, 10), outline=(255, 255, 255, 20), width=1)

    label = "INSIGHT"
    lw = draw.textlength(label, font=font_small)
    draw.text(((W - lw) // 2, card_y + 24), label, fill=(255, 255, 255, 70), font=font_small)

    if hook_lines:
        y = card_y + 80
        for line in hook_lines[:5]:
            lw = draw.textlength(line, font=font_serif)
            draw.text(((W - lw) // 2, y), line, fill=(255, 255, 255, 255), font=font_serif)
            y += 36

    insight = _find_insight(lines)
    if insight:
        draw.line([(362, 560), (662, 560)], fill=(255, 255, 255, 50), width=2)
        il = _wrapped_lines(insight, font_small, max_w, draw)
        y = 600
        for line in il[:2]:
            lw = draw.textlength(line, font=font_small)
            draw.text(((W - lw) // 2, y), line, fill=(255, 255, 255, 120), font=font_small)
            y += 24
