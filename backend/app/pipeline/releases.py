"""Fetch upcoming releases, CFP deadlines, and conferences from iCal feeds."""

import re
from datetime import date, timedelta

import httpx
from icalendar import Calendar

RELEASE_ICAL_URL = "https://peps.python.org/release-schedule.ics"
DEADLINES_ICAL_URL = "https://pythondeadlin.es/python-deadlines.ics"
PYCON_EVENTS_ICAL_URL = "https://www.google.com/calendar/ical/j7gov1cmnqr9tvg14k621j7t5c%40group.calendar.google.com/public/basic.ics"


def _extract_url(description: str) -> str:
    match = re.search(r'href="([^"]+)"', description)
    return match.group(1) if match else "https://pythondeadlin.es"


async def _fetch_ical(client: httpx.AsyncClient, url: str) -> Calendar:
    resp = await client.get(url)
    resp.raise_for_status()
    return Calendar.from_ical(resp.text)


def _event_date(component) -> date | None:
    dt_start = component.get("dtstart")
    if dt_start is None:
        return None
    d = dt_start.dt
    if hasattr(d, "date"):
        d = d.date()
    return d


async def fetch_upcoming_releases() -> list[dict]:
    """Fetch upcoming CPython releases from the PEPs release schedule."""
    today = date.today()
    window_end = today + timedelta(days=30)
    items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            cal = await _fetch_ical(client, RELEASE_ICAL_URL)
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue
                event_date = _event_date(component)
                if not event_date or not (today <= event_date <= window_end):
                    continue

                summary = str(component.get("summary", "")).strip()
                url = str(component.get("url", ""))
                if not url:
                    url = "https://peps.python.org/release-schedule/"

                date_str = event_date.strftime("%b %d")

                items.append(
                    {
                        "section": "upcoming_releases",
                        "title": summary,
                        "url": url,
                        "summary": date_str,
                        "source": "release_schedule",
                        "metadata": {"date": event_date.isoformat()},
                    }
                )
        except Exception as e:
            print(f"  Warning: release schedule failed: {e}")

    items.sort(key=lambda i: i["metadata"]["date"])
    return items


async def fetch_events() -> list[dict]:
    """Fetch CFP deadlines and conferences, combined into one section."""
    today = date.today()
    cfp_end = today + timedelta(days=60)
    conf_end = today + timedelta(days=90)
    items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        # CFP deadlines
        try:
            cal = await _fetch_ical(client, DEADLINES_ICAL_URL)
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue
                event_date = _event_date(component)
                if not event_date or not (today <= event_date <= cfp_end):
                    continue

                summary = str(component.get("summary", "")).strip()
                description = str(component.get("description", ""))

                items.append(
                    {
                        "section": "events",
                        "title": f"\U0001f4cb {summary}",
                        "url": _extract_url(description),
                        "summary": event_date.strftime("%b %d"),
                        "source": "python_deadlines",
                        "metadata": {"date": event_date.isoformat(), "type": "cfp"},
                    }
                )
        except Exception as e:
            print(f"  Warning: CFP deadlines failed: {e}")

        # Conferences
        try:
            cal = await _fetch_ical(client, PYCON_EVENTS_ICAL_URL)
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue
                event_date = _event_date(component)
                if not event_date or not (today <= event_date <= conf_end):
                    continue

                summary = str(component.get("summary", "")).strip()
                description = str(component.get("description", ""))
                url = str(component.get("url", ""))
                if not url:
                    url = (
                        _extract_url(description)
                        if description
                        else "https://pycon.org"
                    )

                items.append(
                    {
                        "section": "events",
                        "title": summary,
                        "url": url,
                        "summary": event_date.strftime("%b %d"),
                        "source": "pycon_calendar",
                        "metadata": {
                            "date": event_date.isoformat(),
                            "type": "conference",
                        },
                    }
                )
        except Exception as e:
            print(f"  Warning: PyCon events failed: {e}")

    # Sort chronologically
    items.sort(key=lambda i: i["metadata"]["date"])
    return items
