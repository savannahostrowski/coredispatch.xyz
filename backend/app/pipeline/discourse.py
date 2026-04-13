"""Fetch active PEP discussions from discuss.python.org/c/peps."""

from datetime import datetime, timedelta, timezone

import httpx

DISCOURSE_URL = "https://discuss.python.org"
PEPS_CATEGORY_ID = 19

MIN_NEW_REPLIES = 2


async def _count_recent_posts(
    client: httpx.AsyncClient, topic_id: int, cutoff: datetime
) -> int:
    """Count posts in a topic created after the cutoff by checking from the end of the stream."""
    try:
        # Get the topic to find the full post stream
        resp = await client.get(f"{DISCOURSE_URL}/t/{topic_id}.json")
        resp.raise_for_status()
        data = resp.json()

        stream = data.get("post_stream", {}).get("stream", [])
        if not stream:
            return 0

        # Check posts from the end in batches of 20
        count = 0
        # Work backwards through the stream
        for i in range(len(stream) - 1, -1, -20):
            batch_ids = stream[max(0, i - 19) : i + 1]
            params = "&".join(f"post_ids[]={pid}" for pid in batch_ids)
            posts_resp = await client.get(
                f"{DISCOURSE_URL}/t/{topic_id}/posts.json?{params}"
            )
            posts_resp.raise_for_status()
            posts = posts_resp.json().get("post_stream", {}).get("posts", [])

            batch_count = 0
            for post in posts:
                created = post.get("created_at", "")
                if created:
                    post_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if post_dt >= cutoff:
                        batch_count += 1

            count += batch_count

            # If this batch had no recent posts, earlier ones won't either
            if batch_count == 0:
                break

        return count
    except Exception:
        return 0


async def fetch_pep_discussions(days: int = 14) -> list[dict]:
    """Fetch PEP discussions with the most new replies in the last 2 weeks."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    candidates: list[dict] = []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        page = 0
        while True:
            url = f"{DISCOURSE_URL}/c/peps/{PEPS_CATEGORY_ID}.json"
            if page > 0:
                url += f"?page={page}"

            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            topics = data.get("topic_list", {}).get("topics", [])
            if not topics:
                break

            found_old = False
            for topic in topics:
                last_posted = topic.get("last_posted_at", "")
                if not last_posted:
                    continue

                last_posted_dt = datetime.fromisoformat(
                    last_posted.replace("Z", "+00:00")
                )
                if last_posted_dt < cutoff:
                    found_old = True
                    continue

                candidates.append(topic)

            if found_old or len(topics) < 30:
                break
            page += 1
            if page > 3:
                break

        # Now count recent posts for each candidate
        items: list[dict] = []
        for topic in candidates:
            topic_id = topic["id"]
            views = topic.get("views", 0)

            # Always include newly created PEP topics
            created_at = topic.get("created_at", "")
            is_new_pep = False
            if created_at:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if created_dt >= cutoff:
                    is_new_pep = True

            new_replies = await _count_recent_posts(client, topic_id, cutoff)
            if new_replies < MIN_NEW_REPLIES and not is_new_pep:
                continue

            if views >= 1000:
                views_str = f"{views / 1000:.1f}k views"
            elif views == 1:
                views_str = f"{views} view"
            else:
                views_str = f"{views} views"

            hot = "\U0001f525 " if new_replies >= 10 else ""
            new_tag = "\U0001f195 " if is_new_pep else ""
            replies_str = "reply" if new_replies == 1 else "replies"

            items.append(
                {
                    "section": "discussions",
                    "title": topic["title"],
                    "url": f"{DISCOURSE_URL}/t/{topic['slug']}/{topic_id}",
                    "summary": f"{new_tag}{hot}{new_replies} new {replies_str} \u00b7 {views_str}",
                    "source": "discourse",
                    "metadata": {
                        "topic_id": topic_id,
                        "new_replies": new_replies,
                        "views": views,
                    },
                }
            )

    items.sort(key=lambda i: i["metadata"]["new_replies"], reverse=True)
    return items[:10]
