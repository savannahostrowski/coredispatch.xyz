"""Fetch recent posts from official Python blogs."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

import os

import httpx
import yaml

MANIFEST_PATH = Path(
    os.environ.get(
        "OFFICIAL_FEEDS_PATH", str(Path(__file__).resolve().parents[3] / "official.yml")
    )
)
DC_NS = "{http://purl.org/dc/elements/1.1/}"


def _load_feeds() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    return yaml.safe_load(MANIFEST_PATH.read_text()) or []


def _parse_rss_date(date_str: str) -> datetime | None:
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


async def fetch_official_news(days: int = 14) -> list[dict]:
    """Fetch recent posts from official Python blogs."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for feed in _load_feeds():
            try:
                resp = await client.get(feed["url"])
                resp.raise_for_status()

                root = ElementTree.fromstring(resp.text)
                channel = root.find("channel")
                if channel is None:
                    continue

                for item_el in channel.findall("item"):
                    title = item_el.findtext("title", "").strip()
                    link = item_el.findtext("link", "").strip()
                    pub_date_str = item_el.findtext("pubDate", "")

                    if pub_date_str:
                        pub_date = _parse_rss_date(pub_date_str)
                        if pub_date and pub_date < cutoff:
                            continue

                    author = item_el.findtext(f"{DC_NS}creator", "").strip()
                    if not author:
                        author = item_el.findtext("author", "").strip()
                    # Strip email format: "noreply@blogger.com (Name)" -> "Name"
                    if "(" in author and author.endswith(")"):
                        author = author[author.index("(") + 1 : -1].strip()
                    display_author = author or feed["name"]

                    items.append(
                        {
                            "section": "official_news",
                            "title": title,
                            "url": link,
                            "summary": f"By {display_author}",
                            "source": "python_blog",
                            "metadata": {
                                "feed": feed["name"],
                                "author": display_author,
                                "published": pub_date_str.strip(),
                            },
                        }
                    )
            except Exception as e:
                print(f"  Warning: failed to fetch {feed['name']}: {e}")

    return items
