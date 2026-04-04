from pathlib import Path

import yaml
from fastapi import APIRouter
from fastapi.responses import Response
from feedgen.feed import FeedGenerator

from app.config import settings

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
    "picks": "Picks of the Week",
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
    issues = []
    for path in EDITIONS_DIR.glob("*.yml"):
        if path.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(path.read_text())
            if data and isinstance(data, dict):
                issues.append(data)
        except Exception:
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
        parts.append(f"<p>{editorial}</p>")

    items = issue.get("items", [])
    for section in SECTION_ORDER:
        section_items = [i for i in items if i.get("section") == section]
        if not section_items:
            continue

        label = SECTION_LABELS.get(section, section)
        parts.append(f"<h3>{label}</h3>")
        parts.append("<ul>")
        for item in section_items:
            title = item.get("title", "")
            url = item.get("url", "")
            summary = item.get("summary", "")
            link = f'<a href="{url}">{title}</a>' if url else title
            if summary:
                parts.append(f"<li>{link} — {summary}</li>")
            else:
                parts.append(f"<li>{link}</li>")
        parts.append("</ul>")

    return "\n".join(parts)


@router.get("/rss")
async def rss_feed():
    fg = FeedGenerator()
    fg.title("Core Dispatch")
    fg.link(href=settings.site_url)
    fg.description(
        "A regular digest of what's happening in CPython — from merged PRs and PEP decisions to community discussions and upcoming events."
    )
    fg.language("en")

    for issue in _load_published_issues()[:20]:
        fe = fg.add_entry()
        fe.title(issue.get("title", ""))
        fe.link(href=f"{settings.site_url}/editions/{issue.get('number', '')}")
        fe.id(f"{settings.site_url}/editions/{issue.get('number', '')}")
        fe.content(_render_issue_html(issue), type="html")

    return Response(content=fg.rss_str(pretty=True), media_type="application/rss+xml")
