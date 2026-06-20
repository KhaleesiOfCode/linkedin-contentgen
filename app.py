import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from drafts import list_drafts, get_draft, update_status, delete_draft, count_by_status, STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED
from content_calendar import get_current_week, get_upcoming_weeks, WEEKS
from config import IMAGES_DIR, POSTS_PER_DAY
from generator import generate_daily_drafts, generate_from_custom_prompt
from prompts import get_daily_prompt

app = Flask(__name__)


@app.context_processor
def inject_calendar():
    override = request.args.get("theme") or os.getenv("OVERRIDE_THEME", "")
    return {
        "current_week": get_current_week(override),
        "upcoming_weeks": get_upcoming_weeks(),
        "all_themes": [w["name"] for w in WEEKS],
        "active_override": override,
        "daily_prompt": get_daily_prompt(override),
    }


@app.route("/")
def index():
    status_filter = request.args.get("status")
    theme_filter = request.args.get("theme", "")
    drafts = list_drafts(status=status_filter if status_filter else None)
    counts = count_by_status()
    return render_template(
        "index.html",
        drafts=drafts,
        counts=counts,
        active_filter=status_filter,
        theme_filter=theme_filter,
    )


@app.route("/generate", methods=["POST"])
def generate():
    theme = request.form.get("theme", "")
    count = int(request.form.get("count", str(POSTS_PER_DAY)))
    custom_prompt = request.form.get("custom_prompt", "").strip()

    if theme:
        os.environ["OVERRIDE_THEME"] = theme

    if custom_prompt:
        generate_from_custom_prompt(custom_prompt, theme or None)
    else:
        generate_daily_drafts(count=count)

    params = f"?theme={theme}" if theme else ""
    return redirect(url_for("index") + params)


@app.route("/prompt")
def prompt():
    theme_filter = request.args.get("theme", "")
    p = get_daily_prompt(theme_filter or None)
    return jsonify(p)


@app.route("/draft/<draft_id>")
def view_draft(draft_id: str):
    draft = get_draft(draft_id)
    if draft is None:
        return "Draft not found", 404
    return render_template("review.html", draft=draft)


@app.route("/draft/<draft_id>/approve", methods=["POST"])
def approve_draft(draft_id: str):
    draft = update_status(draft_id, STATUS_APPROVED)
    if draft is None:
        return "Draft not found", 404
    return redirect(url_for("index"))


@app.route("/draft/<draft_id>/reject", methods=["POST"])
def reject_draft(draft_id: str):
    draft = update_status(draft_id, STATUS_REJECTED)
    if draft is None:
        return "Draft not found", 404
    return redirect(url_for("index"))


@app.route("/draft/<draft_id>/reopen", methods=["POST"])
def reopen_draft(draft_id: str):
    draft = update_status(draft_id, STATUS_PENDING)
    if draft is None:
        return "Draft not found", 404
    return redirect(url_for("index"))


@app.route("/draft/<draft_id>/delete", methods=["POST"])
def remove_draft(draft_id: str):
    delete_draft(draft_id)
    return redirect(url_for("index"))


@app.route("/images/<filename>")
def serve_image(filename: str):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/images/<filename>/download")
def download_image(filename: str):
    return send_from_directory(IMAGES_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, port=5000)
