"""Fetch merged CPython PRs from GitHub.

Uses GitHub Search API with targeted queries to find significant PRs,
plus a file-based search for PRs that touch Doc/whatsnew/ (user-facing changes).
"""

import re
from datetime import date, timedelta

import httpx

from app.config import settings

CPYTHON_REPO = "python/cpython"
GITHUB_API = "https://api.github.com"

BOT_AUTHORS = {"miss-islington", "bedevere-bot"}

# Labels that mean "skip this"
SKIP_LABELS = {"docs", "skip news", "infrastructure"}

# Title patterns that indicate docs/CI noise
SKIP_TITLE_PATTERNS = [
    "document ",
    "documentation",
    "docstring",
    "whatsnew",
    "what's new",
    "run ",
    "ci:",
    "[ci]",
    "check-html",
    "blurb",
]

# Search queries to find signal PRs
SEARCH_QUERIES = [
    'label:"type-feature"',
    'label:"type-security"',
    'label:"type-performance"',
    "comments:>=15",
]


def _should_skip(pr: dict) -> bool:
    """Check if a PR should be filtered out."""
    author = pr.get("user", {}).get("login", "")
    if author in BOT_AUTHORS:
        return True

    title = pr.get("title", "")
    title_lower = title.lower()
    if "backport" in title_lower or title.startswith("[3."):
        return True

    labels = [label["name"] for label in pr.get("labels", [])]
    label_set = {lbl.lower() for lbl in labels}
    if label_set & SKIP_LABELS:
        return True
    if any(pat in title_lower for pat in SKIP_TITLE_PATTERNS):
        return True

    return False


def _pr_to_item(pr: dict, touches_whatsnew: bool = False) -> dict:
    """Convert a GitHub PR to an item dict."""
    labels = [label["name"] for label in pr.get("labels", [])]
    return {
        "section": "merged_prs",
        "title": re.sub(r"^gh-\d+:\s*", "", pr.get("title", "")),
        "url": pr["html_url"],
        "summary": "",
        "source": "github",
        "metadata": {
            "pr_number": pr["number"],
            "author": pr.get("user", {}).get("login", ""),
            "labels": labels,
            "comments": pr.get("comments", 0),
            "touches_whatsnew": touches_whatsnew,
        },
    }


async def _search_prs(client: httpx.AsyncClient, query: str, since: date) -> list[dict]:
    """Run a single search query and return matching PRs."""
    full_query = (
        f"repo:{CPYTHON_REPO} is:pr is:merged merged:>={since.isoformat()} {query}"
    )
    results: list[dict] = []
    page = 1

    while True:
        resp = await client.get(
            f"{GITHUB_API}/search/issues",
            params={
                "q": full_query,
                "per_page": 100,
                "page": page,
                "sort": "updated",
                "order": "desc",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        results.extend(items)

        if len(items) < 100:
            break
        page += 1

    return results


async def _find_whatsnew_prs(client: httpx.AsyncClient, since: date) -> list[dict]:
    """Find PRs that touch Doc/whatsnew/ by checking file lists.

    These are user-facing changes that someone cared enough to document.
    """
    # Get recently merged PRs (broader set)
    prs = await _search_prs(client, "", since)
    whatsnew_prs: list[dict] = []

    for pr in prs:
        if _should_skip(pr):
            continue

        pr_number = pr["number"]
        try:
            resp = await client.get(
                f"{GITHUB_API}/repos/{CPYTHON_REPO}/pulls/{pr_number}/files",
                params={"per_page": 100},
            )
            if resp.status_code != 200:
                continue
            files = [f["filename"] for f in resp.json()]
            if any("whatsnew" in f for f in files):
                # Only include if it touches more than just whatsnew (actual code change)
                non_doc_files = [f for f in files if not f.startswith("Doc/")]
                if non_doc_files:
                    whatsnew_prs.append(pr)
        except Exception:
            continue

    return whatsnew_prs


async def fetch_github_prs(since: date | None = None) -> list[dict]:
    """Fetch significant merged CPython PRs."""
    if since is None:
        since = date.today() - timedelta(days=14)

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "core-dispatch/1.0",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    seen: set[int] = set()
    items: list[dict] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        # 1. Search-based signal PRs (labels, comments)
        for query in SEARCH_QUERIES:
            try:
                prs = await _search_prs(client, query, since)
            except Exception as e:
                print(f"  Warning: search query failed ({query}): {e}")
                continue

            for pr in prs:
                if pr["number"] in seen or _should_skip(pr):
                    continue
                seen.add(pr["number"])
                items.append(_pr_to_item(pr))

        # 2. File-based signal: PRs that touch Doc/whatsnew/
        try:
            whatsnew_prs = await _find_whatsnew_prs(client, since)
            for pr in whatsnew_prs:
                if pr["number"] in seen:
                    # Already included — just mark it
                    for item in items:
                        if item["metadata"]["pr_number"] == pr["number"]:
                            item["metadata"]["touches_whatsnew"] = True
                    continue
                seen.add(pr["number"])
                items.append(_pr_to_item(pr, touches_whatsnew=True))
        except Exception as e:
            print(f"  Warning: whatsnew search failed: {e}")

    # Rank and take top 10
    def _score(item: dict) -> int:
        meta = item["metadata"]
        label_set = {lbl.lower() for lbl in meta.get("labels", [])}
        score = meta.get("comments", 0)
        if "type-feature" in label_set:
            score += 50
        if "type-security" in label_set:
            score += 40
        if "type-performance" in label_set or "performance" in label_set:
            score += 30
        if meta.get("touches_whatsnew"):
            score += 25
        title_lower = item["title"].lower()
        if "add " in title_lower:
            score += 10
        return score

    items.sort(key=_score, reverse=True)
    return items[:10]
