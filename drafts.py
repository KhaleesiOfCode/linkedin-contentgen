import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from config import DRAFTS_DIR

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"


def _draft_path(draft_id: str) -> Path:
    return DRAFTS_DIR / f"{draft_id}.json"


def _next_id() -> str:
    return datetime.now(timezone.utc).strftime("draft_%Y%m%d_%H%M%S_%f")


def create_draft(content: str, topic: str = "", week_theme: str = "", image_file: str | None = None) -> dict:
    draft_id = _next_id()
    draft = {
        "id": draft_id,
        "content": content,
        "topic": topic,
        "week_theme": week_theme,
        "image_file": image_file,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": STATUS_PENDING,
        "approved_at": None,
        "posted_at": None,
    }
    _draft_path(draft_id).write_text(json.dumps(draft, indent=2))
    return draft


def get_draft(draft_id: str) -> Optional[dict]:
    path = _draft_path(draft_id)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_drafts(status: Optional[str] = None) -> list[dict]:
    drafts = []
    for path in sorted(DRAFTS_DIR.glob("draft_*.json"), reverse=True):
        draft = json.loads(path.read_text())
        if status is None or draft["status"] == status:
            drafts.append(draft)
    return drafts


def update_status(draft_id: str, new_status: str) -> Optional[dict]:
    draft = get_draft(draft_id)
    if draft is None:
        return None
    draft["status"] = new_status
    if new_status == STATUS_APPROVED:
        draft["approved_at"] = datetime.now(timezone.utc).isoformat()
    _draft_path(draft_id).write_text(json.dumps(draft, indent=2))
    return draft


def delete_draft(draft_id: str) -> bool:
    path = _draft_path(draft_id)
    if not path.exists():
        return False
    path.unlink()
    from image_gen import delete_image as _del_img
    _del_img(draft_id)
    return True


def count_by_status() -> dict:
    counts = {s: 0 for s in (STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED)}
    for path in DRAFTS_DIR.glob("draft_*.json"):
        draft = json.loads(path.read_text())
        status = draft.get("status", STATUS_PENDING)
        counts[status] = counts.get(status, 0) + 1
    return counts
