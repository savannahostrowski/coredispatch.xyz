"""Fetch recent posts from core team personal blogs for the Core Dev Musings section."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

import os

import httpx
import yaml

MANIFEST_PATH = Path(
    os.environ.get(
        "CORE_BLOGS_PATH", str(Path(__file__).resolve().parents[3] / "core-blogs.yml")
    )
)

ATOM_NS = "{http://www.w3.org/2005/Atom}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"


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


def _parse_rss(
    root: ElementTree.Element, feed_name: str, cutoff: datetime
) -> list[dict]:
    items: list[dict] = []
    channel = root.find("channel")
    if channel is None:
        return items

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
        display_author = author or feed_name

        items.append(
            {
                "section": "musings",
                "title": title,
                "url": link,
                "summary": f"By {display_author}",
                "source": "blog",
                "metadata": {"feed": feed_name, "author": display_author},
            }
        )

    return items


def _parse_atom(
    root: ElementTree.Element, feed_name: str, cutoff: datetime
) -> list[dict]:
    items: list[dict] = []

    for entry in root.findall(f"{ATOM_NS}entry"):
        title = (entry.findtext(f"{ATOM_NS}title") or "").strip()

        link_el = entry.find(f"{ATOM_NS}link[@rel='alternate']")
        if link_el is None:
            link_el = entry.find(f"{ATOM_NS}link")
        link = link_el.get("href", "") if link_el is not None else ""

        updated = (
            entry.findtext(f"{ATOM_NS}updated")
            or entry.findtext(f"{ATOM_NS}published")
            or ""
        )
        if updated:
            pub_date = _parse_rss_date(updated)
            if pub_date and pub_date < cutoff:
                continue

        author_el = entry.find(f"{ATOM_NS}author")
        author = ""
        if author_el is not None:
            author = (author_el.findtext(f"{ATOM_NS}name") or "").strip()
        display_author = author or feed_name

        items.append(
            {
                "section": "musings",
                "title": title,
                "url": link,
                "summary": f"By {display_author}",
                "source": "blog",
                "metadata": {"feed": feed_name, "author": display_author},
            }
        )

    return items


def _parse_feed(content: str, feed_name: str, cutoff: datetime) -> list[dict]:
    root = ElementTree.fromstring(content)

    if root.tag == "rss":
        return _parse_rss(root, feed_name, cutoff)
    elif root.tag == f"{ATOM_NS}feed":
        return _parse_atom(root, feed_name, cutoff)
    if root.find("channel") is not None:
        return _parse_rss(root, feed_name, cutoff)
    return []


def _load_feeds() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    return yaml.safe_load(MANIFEST_PATH.read_text()) or []


async def fetch_musings(days: int = 14) -> list[dict]:
    """Fetch recent posts from core team personal blogs."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    feeds = _load_feeds()
    all_items: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for feed in feeds:
            try:
                resp = await client.get(feed["url"])
                resp.raise_for_status()
                items = _parse_feed(resp.text, feed["name"], cutoff)
                all_items.extend(items)
            except Exception as e:
                print(f"  Warning: failed to fetch {feed['name']}: {e}")

    # Deduplicate by title (cross-posts)
    seen: dict[str, dict] = {}
    for item in all_items:
        key = _normalize_title(item["title"])
        if key not in seen:
            seen[key] = item

    return list(seen.values())


def _normalize_title(title: str) -> str:
    key = title.strip().lower()
    return (
        key.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
