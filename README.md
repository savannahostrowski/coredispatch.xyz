# Core Dispatch

A regular digest of what's happening in CPython, from merged PRs and PEP decisions to community discussions and upcoming events.

**Live at [coredispatch.xyz](https://coredispatch.xyz)**

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [bun](https://bun.sh/)
- A GitHub token with public repo read access (for the generating the edition draft)

### Setup

```bash
# Install dependencies
cd backend && uv sync && cd ..
cd frontend && bun install && cd ..

# Add your GitHub token
echo 'GITHUB_TOKEN=ghp_...' > backend/.env
```

### Run

```bash
./scripts/dev.sh
```

This starts the FastAPI backend on `:8000` and the Astro frontend on `:4321`. The frontend proxies `/api` requests to the backend.

### Generate a draft edition

```bash
cd backend && uv run python -m app.pipeline.run
```

This fetches data from all sources and writes a YAML file to `drafts/`. Preview it at `http://localhost:4321/staging`.

## Publishing Workflow

Every Friday, a new edition's skeleton is generated automatically by GitHub Actions and opened as a draft PR. Editors merge the draft and then review, add notes and picks, and take a solid editorial pass on `main`. Once the draft is ready (usually by the following Thursday), it's moved from `drafts/` to `editions/` to publish. Buttondown picks up the new edition via RSS and sends it to subscribers.

## Content

Each edition is a YAML file with auto-generated and hand-curated sections.

### Auto-generated sections

These are populated by the pipeline every Friday:

| Section | Source |
|---------|--------|
| **Upcoming Releases** | [peps.python.org](https://peps.python.org) release schedule iCal |
| **Official News** | Python Blog + PyPI Blog (configured in `official.yml`) |
| **PEP Updates** | Merged PRs in [python/peps](https://github.com/python/peps) that change a PEP's status |
| **Steering Council Updates** | PSC meeting summaries from [discuss.python.org/c/committers](https://discuss.python.org/c/committers) |
| **Merged PRs** | Draft is created with high-traffic PRs but this needs manual curation to remove noise and add context |
| **Discussion** | Most active PEP discussions on Discourse, ranked by new replies |
| **Core Dev Musings** | Personal blogs and podcasts (configured in `core-blogs.yml`) |
| **Upcoming CFPs & Conferences** | [pythondeadlin.es](https://pythondeadlin.es) + PyCon event calendar |

### Hand-curated sections

These are added during editorial review:

| Section | Description |
|---------|-------------|
| **Community** | Links, talks, and tools submitted by the community |
| **One More Thing** | A quote or fun post — top-level `quote` field in the YAML |
| **Editorial Notes** | The intro paragraph — top-level `editorial_notes` field |
| **Credits** | Who put this edition together — top-level `credits` field |

## Contributing

### Submit a link

Found something the Python community should know about? [Open a GitHub issue](https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml) with the link, a title, and which section it belongs in. Accepted submissions appear in the **Community** section.

### Submit a quote

Have a great quote for **One More Thing**? [Submit it as an issue](https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml&title=%5BQuote%5D+) with the text, author, and a link to the source.

### Add a blog feed

Are you a core developer or regular Python contributor with a blog? Open a PR to add your feed to `core-blogs.yml`:

```yaml
- name: Your Name
  url: https://yourblog.com/tags/python/feed.xml
```

> Note: If you have tags or categories, it's best to link to a feed that filters for Python-related content. Otherwise, all your posts will be included, which may not be relevant to the newsletter. We will review the feed and may remove posts that are not relevant.

### Add an official feed

If an official Python project has a blog (like the PSF or a working group), open a PR to add it to `official.yml`.

## Editing an Edition

Want to help curate and edit the next edition? Here's what we need help with!

1. **Write editorial notes** — a 2-3 sentence intro that ties the highlights together. What's the big story this week?
2. **Remove noise** — delete items that aren't interesting or relevant. Less is more.
3. **Add community picks** — add items with `section: picks` from submitted issues or things you've found
4. **Add a quote** — fill in the `quote` field with something fun, insightful, or mass-reply-inducing
5. **Add credits** — list everyone who contributed to this edition in the `credits` field
6. **Review PR titles** — the auto-generated PR titles are raw GitHub titles. Rewrite to be human-readable when needed.