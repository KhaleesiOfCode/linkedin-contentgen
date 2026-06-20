"""Run daily generation on a schedule.

Usage:
  python scheduler.py           # Generate drafts for today
  python scheduler.py --watch   # Generate now, then daily at 08:00
"""
import sys
import time
import schedule
from generator import generate_daily_drafts


def generate_and_report():
    drafts = generate_daily_drafts()
    print(f"[{time.strftime('%Y-%m-%d %H:%M')}] Generated {len(drafts)} draft(s)")
    for d in drafts:
        print(f"  -> {d['id']} [{d['topic']}]")
    return drafts


def main():
    if "--watch" in sys.argv:
        generate_and_report()
        schedule.every().day.at("08:00").do(generate_and_report)
        print("Scheduler running. Next generation at 08:00 daily. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        generate_and_report()


if __name__ == "__main__":
    main()
