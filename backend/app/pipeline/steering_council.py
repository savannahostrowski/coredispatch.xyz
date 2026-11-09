"""Fetch Steering Council meeting summaries from discuss.python.org/c/committers."""

from datetime import UTC, datetime, timedelta

import httpx

DISCOURSE_URL = "https://discuss.python.org"
COMMITTERS_CATEGORY_ID = 5


async def fetch_steering_council(days: int = 14) -> list[dict]:
    """Fetch recent PSC Meeting Summary topics from the committers category."""
    cutoff = datetime.now(UTC) - timedelta(days=days)
    items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{DISCOURSE_URL}/c/committers/{COMMITTERS_CATEGORY_ID}.json"
        )
        resp.raise_for_status()
        data = resp.json()

        for topic in data.get("topic_list", {}).get("topics", []):
            title = topic.get("title", "")

            # Only PSC meeting summaries
            if (
                "psc meeting summary" not in title.lower()
                and "steering council" not in title.lower()
            ):
                continue

            created_at = topic.get("created_at", "")
            if created_at:
                created_dt = datetime.fromisoformat(created_at)
                if created_dt < cutoff:
                    continue

            topic_id = topic["id"]
            items.append(
                {
                    "section": "steering_council",
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
