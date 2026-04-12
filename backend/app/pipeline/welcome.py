"""Fetch new core team member announcements from discuss.python.org/c/committers."""

import re
from datetime import datetime, timedelta, timezone

import httpx

DISCOURSE_URL = "https://discuss.python.org"
COMMITTERS_CATEGORY_ID = 5

WELCOME_PATTERNS = [
    re.compile(r"welcome\s+.+\s+to\s+the", re.IGNORECASE),
    re.compile(r"vote\s+to\s+promote", re.IGNORECASE),
    re.compile(r"please\s+welcome", re.IGNORECASE),
    re.compile(r"new\s+core\s+(dev|team)", re.IGNORECASE),
    re.compile(r"new\s+triag(e|er)", re.IGNORECASE),
]


async def fetch_welcome(days: int = 14) -> list[dict]:
    """Fetch recent welcome/promotion topics from the committers category."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{DISCOURSE_URL}/c/committers/{COMMITTERS_CATEGORY_ID}.json"
        )
        resp.raise_for_status()
        data = resp.json()

        for topic in data.get("topic_list", {}).get("topics", []):
            title = topic.get("title", "")

            if not any(p.search(title) for p in WELCOME_PATTERNS):
                continue

            created_at = topic.get("created_at", "")
            if created_at:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if created_dt < cutoff:
                    continue

            topic_id = topic["id"]
            items.append(
                {
                    "section": "welcome",
                    "title": title,
                    "url": f"{DISCOURSE_URL}/t/{topic['slug']}/{topic_id}",
                    "summary": "",
                    "source": "discourse",
                    "metadata": {
                        "topic_id": topic_id,
                        "category": "committers",
                    },
                }
            )

    return items
