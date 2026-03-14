"""
reddit_service.py — All Reddit API interactions live here.

Uses the public JSON endpoints (no OAuth required) with a custom User-Agent
to comply with Reddit's API rules and avoid rate-limiting.

All functions are synchronous and must be called via asyncio.to_thread()
from async contexts to avoid blocking the event loop.
"""

import logging
from dataclasses import dataclass

import requests

import config

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 10


@dataclass
class RedditPost:
    """Lightweight representation of a Reddit post."""
    post_id: str
    title: str
    author: str
    score: int
    url: str        # permalink to the Reddit discussion thread
    subreddit: str


def _get(url: str) -> dict | None:
    """
    Perform a GET request to a Reddit JSON endpoint.

    Retries once on transient failures. Returns None on permanent failure
    (e.g. 404) or after the retry is exhausted. Callers treat None as a
    failed request and surface an error to the user.
    """
    headers = {"User-Agent": config.REDDIT_USER_AGENT}
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=_REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            logger.warning("Reddit HTTP %s for %s (attempt %d)", status, url, attempt + 1)
            # 404 means the resource genuinely doesn't exist — no point retrying
            if status == 404:
                return None
        except requests.exceptions.RequestException as exc:
            logger.warning("Reddit request failed (attempt %d): %s", attempt + 1, exc)

    return None


def _parse_posts(data: dict) -> list[RedditPost]:
    """Extract RedditPost objects from a Reddit listing response."""
    posts: list[RedditPost] = []
    for child in data.get("data", {}).get("children", []):
        post_data = child.get("data", {})
        # Skip stickied posts (mod announcements) — they're not organic content
        if post_data.get("stickied"):
            continue
        posts.append(
            RedditPost(
                post_id=post_data.get("id", ""),
                title=post_data.get("title", "No title"),
                author=post_data.get("author", "[deleted]"),
                score=post_data.get("score", 0),
                url=f"https://www.reddit.com{post_data.get('permalink', '')}",
                subreddit=post_data.get("subreddit", ""),
            )
        )
    return posts


def subreddit_exists(subreddit: str) -> bool:
    """Return True if the subreddit is publicly accessible."""
    url = config.REDDIT_TOP_URL.format(subreddit=subreddit)
    return _get(url) is not None


def get_top_posts(subreddit: str) -> list[RedditPost] | None:
    """
    Fetch the top 5 posts of the day from a subreddit.

    Returns a list of RedditPost objects, or None if the request failed.
    """
    url = config.REDDIT_TOP_URL.format(subreddit=subreddit)
    data = _get(url)
    if data is None:
        return None
    return _parse_posts(data)[:5]


def get_newest_post(subreddit: str) -> RedditPost | None:
    """
    Fetch the single newest post from a subreddit.

    Used by the scheduler to detect new activity.
    Returns None if the request failed or the subreddit has no posts.
    """
    url = config.REDDIT_NEW_URL.format(subreddit=subreddit)
    data = _get(url)
    if data is None:
        return None
    posts = _parse_posts(data)
    return posts[0] if posts else None
