"""Generate today's drafts.

Usage:
  python run.py                         # Default (1 draft, current week theme)
  python run.py --count 3               # 3 drafts
  python run.py --theme "AI & ML"       # Force a specific theme
  python run.py --theme "Data Engineering" --count 2
"""
import sys
import os
from config import POSTS_PER_DAY
from generator import generate_daily_drafts
from content_calendar import get_current_week

count = POSTS_PER_DAY
if "--count" in sys.argv:
    idx = sys.argv.index("--count")
    count = int(sys.argv[idx + 1])

override = None
if "--theme" in sys.argv:
    idx = sys.argv.index("--theme")
    override = sys.argv[idx + 1]
    os.environ["OVERRIDE_THEME"] = override

week = get_current_week()
drafts = generate_daily_drafts(count=count)
print(f"\n{'='*50}")
print(f"Theme: {week['name']}{' (override)' if override else ''} | Generated {len(drafts)} draft(s)")
for d in drafts:
    print(f"  [{d['id']}] {d['topic']}")
print(f"\nStart the web UI to review:")
print(f"  python app.py")
print(f"  -> http://localhost:5000")
print(f"{'='*50}")
