"""
formatting.py — All Telegram message templates in one place.

All functions return strings ready to be passed with parse_mode="Markdown"
(legacy Markdown, not MarkdownV2 — simpler escaping, sufficient for this use case).
"""

import config
from reddit_service import RedditPost


def _score_bar(score: int) -> str:
    """Return a short visual indicator for the post score."""
    if score >= 10_000:
        return "🔥🔥🔥"
    if score >= 1_000:
        return "🔥🔥"
    if score >= 100:
        return "🔥"
    return "⬆️"


def _escape_markdown(text: str) -> str:
    """
    Escape characters that break legacy Telegram Markdown.

    Asterisks and underscores break bold/italic; backticks break code spans.
    Square brackets must also be escaped — an unescaped [ or ] inside a link
    label like [title](url) would produce a parse error or garbled output.
    """
    for char in ["[", "]", "*", "_", "`"]:
        text = text.replace(char, f"\\{char}")
    return text


def format_welcome() -> str:
    return (
        "👋 *Welcome to Reddit Monitor Bot!*\n\n"
        "I keep an eye on subreddits and ping you the moment a new post appears.\n\n"
        "Here's what I can do:\n"
        "• 📌 Fetch the *top posts of the day* from any subreddit\n"
        "• 🔔 *Monitor* a subreddit and alert you on new posts\n"
        "• ✅ You can subscribe to *one subreddit at a time*\n\n"
        "Type /help to see all available commands."
    )


def format_help() -> str:
    minutes = config.CHECK_INTERVAL // 60
    return (
        "📋 *Available Commands*\n\n"
        "*/start* — Welcome message\n"
        "*/help* — Show this help\n\n"
        "*/top <subreddit>*\n"
        "  Fetch the top 5 posts of the day\n"
        "  _Example:_ `/top worldnews`\n\n"
        "*/subscribe <subreddit>*\n"
        "  Start monitoring a subreddit for new posts\n"
        "  _Example:_ `/subscribe programming`\n\n"
        "*/unsubscribe*\n"
        "  Stop monitoring the current subreddit\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🔔 Monitoring checks every *{minutes} minutes* for new posts."
    )


def format_top_posts(posts: list[RedditPost], subreddit: str) -> str:
    lines = [f"📌 *Top posts today on r/{subreddit}*\n"]
    for i, post in enumerate(posts, start=1):
        title = _escape_markdown(post.title)
        lines.append(
            f"*{i}.* [{title}]({post.url})\n"
            f"   👤 u/{post.author}  •  {_score_bar(post.score)} {post.score:,} pts\n"
        )
    return "\n".join(lines)


def format_alert_post(post: RedditPost, subreddit: str) -> str:
    title = _escape_markdown(post.title)
    return (
        f"🔔 *New post on r/{subreddit}*\n\n"
        f"📌 [{title}]({post.url})\n\n"
        f"👤 Posted by u/{post.author}\n"
        f"{_score_bar(post.score)} Score: {post.score:,}"
    )


def format_subscribe_success(subreddit: str) -> str:
    minutes = config.CHECK_INTERVAL // 60
    return (
        f"✅ *Subscribed to r/{subreddit}!*\n\n"
        f"I'll check for new posts every *{minutes} minutes* and alert you here.\n\n"
        "Use /unsubscribe to stop monitoring."
    )


def format_already_subscribed(subreddit: str) -> str:
    return (
        f"ℹ️ You're already monitoring *r/{subreddit}*.\n\n"
        "Use /unsubscribe first to switch to a different subreddit."
    )


def format_unsubscribe_success(subreddit: str) -> str:
    return (
        f"✅ *Unsubscribed from r/{subreddit}.*\n\n"
        "You won't receive any more alerts.\n"
        "Use /subscribe to start monitoring again."
    )


def format_not_subscribed() -> str:
    return (
        "❌ *You have no active subscription.*\n\n"
        "Use `/subscribe <subreddit>` to start monitoring a subreddit."
    )


def format_subreddit_not_found(subreddit: str) -> str:
    return (
        f"❌ *r/{subreddit} not found.*\n\n"
        "The subreddit may be:\n"
        "• Misspelled\n"
        "• Private or banned\n"
        "• Restricted to logged-in users\n\n"
        "Please double-check the name and try again."
    )


def format_api_error() -> str:
    return (
        "❌ *Could not reach Reddit.*\n\n"
        "The Reddit API is temporarily unavailable.\n"
        "Please try again in a few moments."
    )


def format_missing_argument(command: str, example: str) -> str:
    return (
        f"⚠️ *Missing argument for /{command}*\n\n"
        f"Usage: `/{command} <subreddit>`\n"
        f"_Example:_ `{example}`"
    )
