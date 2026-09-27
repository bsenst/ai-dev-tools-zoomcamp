#!/usr/bin/env python3
"""
Additional verification: Test the express-1002 endpoint and analyze the bug.
"""

import json
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen
from urllib.error import HTTPError


def test_express_order():
    """Test express-1002 lookup - should return 500 error."""
    url = "http://localhost:8000/api/orders/express-1002"
    try:
        with urlopen(url, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()


def analyze_bug():
    """Analyze the root cause of the express-1002 500 error."""
    print("=" * 60)
    print("BUG ANALYSIS: express-1002 returns 500 Internal Server Error")
    print("=" * 60)

    # From app/main.py order_detail() function:
    #   placed_at = datetime.fromisoformat(order["created_at"])
    #   estimated_at = placed_at.replace(day=placed_at.day + 2)
    #
    # The order express-1002 was created with created_at = previous_month_end
    # which is the last day of the previous month.
    #
    # If today is September 27, 2026:
    #   previous_month_end = August 31, 2026
    #   placed_at.day = 31
    #   placed_at.day + 2 = 33
    #   August doesn't have 33 days -> ValueError -> 500 error

    now = datetime.now(timezone.utc)
    previous_month_end = now.replace(day=1) - timedelta(days=1)

    print(f"\nCurrent date: {now.date()}")
    print(f"Order express-1002 created_at: {previous_month_end.date()}")
    print(f"placed_at.day = {previous_month_end.day}")
    print(f"placed_at.day + 2 = {previous_month_end.day + 2}")

    month_name = previous_month_end.strftime("%B")
    print(f"\nAttempting: {month_name} {previous_month_end.day + 2}, {previous_month_end.year}")
    print(f"Max days in {month_name}: {previous_month_end.day} (it's the last day)")

    try:
        estimated_at = previous_month_end.replace(day=previous_month_end.day + 2)
    except ValueError as e:
        print(f"\nValueError raised: {e}")
        print("This causes a 500 Internal Server Error in the API.")

    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("The express delivery date calculation tried to use a day")
    print("that does not exist in that month.")
    print("=" * 60)


if __name__ == "__main__":
    status, body = test_express_order()
    print(f"GET /api/orders/express-1002 -> HTTP {status}")
    print(f"Response: {body}")
    print()
    analyze_bug()