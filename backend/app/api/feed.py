import re
from html import escape
from pathlib import Path

import logging
import yaml
from fastapi import APIRouter, Request
from fastapi.responses import Response
from feedgen.feed import FeedGenerator

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

EDITIONS_DIR = Path(settings.editions_dir)

SECTION_LABELS = {
    "upcoming_releases": "Upcoming Releases",
    "official_news": "Official News",
    "pep_updates": "PEP Updates",
    "steering_council": "Steering Council Updates",
    "merged_prs": "Merged PRs",
    "discussions": "Discussion",
    "events": "Upcoming CFPs & Conferences",
    "musings": "Core Dev Musings",
    "picks": "Community",
}

SECTION_ORDER = [
    "upcoming_releases",
    "official_news",
    "pep_updates",
    "steering_council",
    "merged_prs",
    "discussions",
    "musings",
    "events",
    "picks",
]


def _load_published_issues() -> list[dict]:
    if not EDITIONS_DIR.exists():
        return []
    issues = []
    for path in EDITIONS_DIR.glob("*.yml"):
        if path.name.startswith("_") or path.name.startswith("."):
            continue
        try:
            data = yaml.safe_load(path.read_text())
            if data and isinstance(data, dict):
                issues.append(data)
        except yaml.YAMLError, OSError:
            continue
    issues.sort(key=lambda i: i.get("number", 0), reverse=True)
    return issues


def _render_issue_html(issue: dict) -> str:
    """Render an issue's content as HTML for RSS."""
    parts: list[str] = []

    editorial = (
        (issue.get("editorial_notes") or "")
        .replace("<!--", "")
        .replace("-->", "")
        .strip()
    )
    if editorial:
        for para in editorial.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            # Convert markdown links to HTML before escaping
            para = re.sub(
                r"\[([^\]]+)\]\(([^)]+)\)",
                lambda m: f'<a href="{escape(m.group(2))}">{escape(m.group(1))}</a>',
                para,
            )
            # Escape everything except our generated <a> tags
            parts_inline = re.split(r"(<a [^>]+>[^<]*</a>)", para)
            para = "".join(
                p if p.startswith("<a ") else escape(p) for p in parts_inline
            )
            para = re.sub(r"`([^`]+)`", r"<code>\1</code>", para)
            parts.append(f"<p>{para}</p>")

    items = issue.get("items", [])
    for section in SECTION_ORDER:
        section_items = [i for i in items if i.get("section") == section]
        if not section_items:
            continue

        label = SECTION_LABELS.get(section, section)
        parts.append(f"<h3>{escape(label)}</h3>")
        parts.append("<ul>")
        for item in section_items:
            title = escape(item.get("title", ""))
            url = escape(item.get("url", ""))
            summary = escape(item.get("summary", ""))
            link = f'<a href="{url}">{title}</a>' if url else title
            if summary:
                parts.append(f"<li>{link} — {summary}</li>")
            else:
                parts.append(f"<li>{link}</li>")
        parts.append("</ul>")

    return "\n".join(parts)


@router.get("/rss")
@router.head("/rss")
async def rss_feed(request: Request):
    user_agent = request.headers.get("user-agent", "")
    if user_agent:
        logger.info("RSS fetch: %s", user_agent)
    fg = FeedGenerator()
    fg.title("Core Dispatch")
    fg.link(href=settings.site_url)
    fg.link(href=f"{settings.site_url}/api/feed/rss", rel="self")
    fg.description(
        "A regular digest of what's happening in CPython — from merged PRs and PEP decisions to community discussions and upcoming events."
    )
    fg.language("en")

    for issue in _load_published_issues()[:20]:
        fe = fg.add_entry()
        fe.title(issue.get("title", ""))
        fe.link(href=f"{settings.site_url}/editions/{issue.get('number', '')}")
        fe.id(f"{settings.site_url}/editions/{issue.get('number', '')}")
        editorial = (
            (issue.get("editorial_notes") or "")
            .replace("<!--", "")
            .replace("-->", "")
            .strip()
        )
        fe.description(editorial[:300] if editorial else issue.get("title", ""))
        fe.content(_render_issue_html(issue), type="html")
        period_end = issue.get("period_end", "")
        if period_end:
            fe.published(f"{period_end}T00:00:00+00:00")
            fe.updated(f"{period_end}T00:00:00+00:00")

    return Response(
        content=fg.rss_str(pretty=True),
        media_type="application/rss+xml; charset=utf-8",
    )
