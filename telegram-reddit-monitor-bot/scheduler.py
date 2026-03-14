"""
scheduler.py — Periodic job that checks for new Reddit posts and alerts users.

Each subscribed chat gets its own JobQueue job so subscriptions are
independent.  We store only the last-seen post ID in memory; the bot does
not use a database because a restart intentionally re-sends the very latest
post (a deliberate design trade-off to keep the project dependency-free).
"""

import asyncio
import logging
from typing import Any

from telegram.ext import ContextTypes

import config
import reddit_service
from formatting import format_alert_post

logger = logging.getLogger(__name__)

# { chat_id: last_seen_post_id }
_last_seen: dict[int, str] = {}

_JOB_PREFIX = "reddit_monitor_"


def _job_name(chat_id: int) -> str:
    return f"{_JOB_PREFIX}{chat_id}"


async def _check_new_posts(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Callback executed by JobQueue every CHECK_INTERVAL seconds.

    context.job.data holds {"chat_id": int, "subreddit": str}.
    reddit_service functions are synchronous (requests-based), so they are
    dispatched to a thread pool to avoid blocking the event loop.
    """
    job_data: dict[str, Any] = context.job.data  # type: ignore[index]
    chat_id: int = job_data["chat_id"]
    subreddit: str = job_data["subreddit"]

    logger.debug("Checking new posts for chat %s on r/%s", chat_id, subreddit)

    post = await asyncio.to_thread(reddit_service.get_newest_post, subreddit)

    if post is None:
        # Transient API failure — skip this cycle silently
        return

    last_id = _last_seen.get(chat_id)

    if last_id is None:
        # First run after subscribing — seed the state without alerting the user
        _last_seen[chat_id] = post.post_id
        logger.info("Seeded last_seen for chat %s: %s", chat_id, post.post_id)
        return

    if post.post_id != last_id:
        _last_seen[chat_id] = post.post_id
        logger.info("New post detected on r/%s: %s", subreddit, post.post_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=format_alert_post(post, subreddit),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )


def start_monitoring(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    subreddit: str,
) -> None:
    """
    Schedule a repeating job to monitor a subreddit for a specific chat.

    Cancels any existing job for this chat first so there's never more than
    one active subscription per user.
    """
    stop_monitoring(context, chat_id)

    context.job_queue.run_repeating(  # type: ignore[union-attr]
        callback=_check_new_posts,
        interval=config.CHECK_INTERVAL,
        first=5,  # Short delay so the seed run happens quickly after subscribing
        data={"chat_id": chat_id, "subreddit": subreddit},
        name=_job_name(chat_id),
        chat_id=chat_id,
    )
    logger.info(
        "Started monitoring r/%s for chat %s (interval: %ss)",
        subreddit, chat_id, config.CHECK_INTERVAL,
    )


def stop_monitoring(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> bool:
    """
    Cancel the monitoring job for a chat.

    Returns True if a job was found and cancelled, False if no subscription
    was active.
    """
    jobs = context.job_queue.get_jobs_by_name(_job_name(chat_id))  # type: ignore[union-attr]
    if not jobs:
        return False

    for job in jobs:
        job.schedule_removal()

    _last_seen.pop(chat_id, None)
    logger.info("Stopped monitoring for chat %s", chat_id)
    return True


def current_subreddit(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> str | None:
    """Return the subreddit being monitored for this chat, or None."""
    jobs = context.job_queue.get_jobs_by_name(_job_name(chat_id))  # type: ignore[union-attr]
    if not jobs:
        return None
    job_data: dict[str, Any] = jobs[0].data  # type: ignore[index]
    return job_data.get("subreddit")
