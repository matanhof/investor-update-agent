"""
Schedule helper — determines which step to run based on days before end of month.

Schedule:
  5 days before end of month → outreach
  4 days before              → check
  3 days before              → nudge
  2 days before              → escalate
  1 day before               → draft
  Last day of month          → deliver
"""

import calendar
from datetime import datetime


def get_step_for_today():
    today = datetime.utcnow()
    year = today.year
    month = today.month
    day = today.day

    last_day = calendar.monthrange(year, month)[1]
    days_before_end = last_day - day

    step_map = {
        5: "outreach",
        4: "check",
        3: "nudge",
        2: "escalate",
        1: "draft",
        0: "deliver",
    }

    return step_map.get(days_before_end, "skip")


if __name__ == "__main__":
    print(get_step_for_today())
