"""Pipeline: fetch data from all sources, write a draft edition YAML file.

Called by the GHA cron workflow. Outputs a YAML file to drafts/ directory
which the GHA then commits and opens as a draft PR.
"""

import asyncio
from datetime import date, timedelta
from pathlib import Path

import yaml

from app.pipeline.blogs import fetch_official_news
from app.pipeline.discourse import fetch_pep_discussions
from app.pipeline.github_prs import fetch_github_prs
from app.pipeline.musings import fetch_musings
from app.pipeline.peps import fetch_pep_updates
from app.pipeline.releases import fetch_events, fetch_upcoming_releases
from app.pipeline.steering_council import fetch_steering_council


def _normalize_title(title: str) -> str:
    key = title.strip().lower()
    return (
        key.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def week_slug(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-w{week:02d}"


def _scan_yml_dir(directory: Path) -> list[dict]:
    """Load all YAML issue files from a directory."""
    results = []
    if not directory.exists():
        return results
    for f in directory.glob("*.yml"):
        if f.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(f.read_text())
            if data and isinstance(data.get("number"), int):
                results.append(data)
        except Exception:
            continue
    return results


def _last_issue_date(repo_root: Path) -> date | None:
    """Find the period_end of the most recent issue across editions/ and drafts/."""
    all_issues = _scan_yml_dir(repo_root / "editions") + _scan_yml_dir(
        repo_root / "drafts"
    )
    if not all_issues:
        return None
    latest = max(all_issues, key=lambda d: d.get("number", 0))
    end = latest.get("period_end", "")
    return date.fromisoformat(end) if end else None


def _next_issue_number(repo_root: Path) -> int:
    """Find the next issue number across editions/ and drafts/."""
    all_issues = _scan_yml_dir(repo_root / "editions") + _scan_yml_dir(
        repo_root / "drafts"
    )
    if not all_issues:
        return 1
    return max(d.get("number", 0) for d in all_issues) + 1


async def run_pipeline(issues_dir: Path, since: date | None = None):
    repo_root = issues_dir.parent

    period_end = date.today()
    slug = week_slug(period_end)
    output_path = issues_dir / f"{slug}.yml"

    updateable_issue = None
    if output_path.exists():
        updateable_issue = yaml.safe_load(output_path.read_text())
        if not since:
            since = date.fromisoformat(updateable_issue["period_start"])

    if since is None:
        # Look back to the last issue's end date, or default to 14 days
        last_end = _last_issue_date(repo_root)
        if last_end:
            since = last_end
        else:
            since = date.today() - timedelta(days=14)

    period_start = since

    print(f"Fetching data for {slug} ({period_start} to {period_end})...")

    all_generate_items: list[dict] = []

    days_back = (period_end - period_start).days

    fetchers = [
        ("Upcoming releases", fetch_upcoming_releases()),
        ("Official news", fetch_official_news(days=days_back)),
        ("PEP updates", fetch_pep_updates(since)),
        ("Steering Council", fetch_steering_council(days=days_back)),
        ("PRs", fetch_github_prs(since)),
        ("PEP discussions", fetch_pep_discussions(days=days_back)),
        ("Events", fetch_events()),
        ("Core dev musings", fetch_musings(days=days_back)),
    ]

    for name, coro in fetchers:
        try:
            items = await coro
            print(f"  -> {len(items)} {name}")
            all_generate_items.extend(items)
        except Exception as e:
            print(f"  !! {name} failed: {e}")

    # Dedupe across sections by title — prefer earlier sections (official_news > musings)
    seen_titles: set[str] = set()
    deduped: list[dict] = []
    for item in all_generate_items:
        key = _normalize_title(item["title"])
        if key in seen_titles:
            continue
        seen_titles.add(key)
        deduped.append(item)
    all_generate_items = deduped

    issue_number = (
        _next_issue_number(repo_root)
        if not updateable_issue
        else updateable_issue["number"]
    )

    hand_curated_sections = {
        "editorial_notes": "<!-- Write your editorial notes here -->\n",
        "quote": {"text": "<!-- Add a quote here -->", "author": "", "url": ""},
        "credits": [],
    }
    hand_curated_items: list[dict] = []
    if updateable_issue:
        hand_curated_sections = {k: updateable_issue[k] for k in hand_curated_sections}
        hand_curated_items = [
            item
            for item in updateable_issue["items"]
            if item["section"] == "picks" or item["source"] == "manual"
        ]

    issue = {
        "number": issue_number,
        "title": f"Core Dispatch #{issue_number}",
        "slug": slug,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        **hand_curated_sections,
        "items": all_generate_items + hand_curated_items,
    }

    output_path.write_text(
        yaml.dump(issue, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )
    print(
        f"{'Wrote' if not updateable_issue else 'Updated'} {output_path} with {len(all_generate_items)} items"
    )
    return output_path


def main():
    repo_root = Path(__file__).resolve().parents[3]  # backend/app/pipeline -> repo root
    drafts_dir = repo_root / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    asyncio.run(run_pipeline(drafts_dir))


if __name__ == "__main__":
    main()
