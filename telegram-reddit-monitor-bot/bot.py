"""
bot.py — Entry point and command handlers for the Reddit Monitor Bot.

Run this file to start the bot:
    python bot.py

python-telegram-bot v20+ is fully async. Handlers must not call blocking I/O
directly — all reddit_service calls are dispatched via asyncio.to_thread().
"""

import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import config
import reddit_service
import scheduler
from formatting import (
    format_api_error,
    format_already_subscribed,
    format_help,
    format_missing_argument,
    format_not_subscribed,
    format_subscribe_success,
    format_subreddit_not_found,
    format_top_posts,
    format_unsubscribe_success,
    format_welcome,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def _parse_subreddit(raw: str) -> str:
    """Strip whitespace and the optional 'r/' prefix from user input."""
    return raw.strip().removeprefix("r/")


# ── Command handlers ───────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — Send a welcome message."""
    await update.message.reply_text(format_welcome(), parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — Show available commands."""
    await update.message.reply_text(format_help(), parse_mode="Markdown")


async def top_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/top <subreddit> — Fetch the top 5 posts of the day."""
    if not context.args:
        await update.message.reply_text(
            format_missing_argument("top", "/top python"),
            parse_mode="Markdown",
        )
        return

    subreddit = _parse_subreddit(context.args[0])
    await update.message.chat.send_action("typing")

    exists = await asyncio.to_thread(reddit_service.subreddit_exists, subreddit)
    if not exists:
        await update.message.reply_text(
            format_subreddit_not_found(subreddit), parse_mode="Markdown"
        )
        return

    posts = await asyncio.to_thread(reddit_service.get_top_posts, subreddit)
    if posts is None:
        await update.message.reply_text(format_api_error(), parse_mode="Markdown")
        return

    if not posts:
        await update.message.reply_text(
            f"ℹ️ No posts found in *r/{subreddit}* today.", parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        format_top_posts(posts, subreddit),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/subscribe <subreddit> — Start monitoring a subreddit."""
    if not context.args:
        await update.message.reply_text(
            format_missing_argument("subscribe", "/subscribe worldnews"),
            parse_mode="Markdown",
        )
        return

    subreddit = _parse_subreddit(context.args[0])
    chat_id = update.effective_chat.id

    current = scheduler.current_subreddit(context, chat_id)
    if current and current.lower() == subreddit.lower():
        await update.message.reply_text(
            format_already_subscribed(subreddit), parse_mode="Markdown"
        )
        return

    await update.message.chat.send_action("typing")

    exists = await asyncio.to_thread(reddit_service.subreddit_exists, subreddit)
    if not exists:
        await update.message.reply_text(
            format_subreddit_not_found(subreddit), parse_mode="Markdown"
        )
        return

    scheduler.start_monitoring(context, chat_id, subreddit)
    await update.message.reply_text(
        format_subscribe_success(subreddit), parse_mode="Markdown"
    )


async def unsubscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/unsubscribe — Stop monitoring the current subreddit."""
    chat_id = update.effective_chat.id
    current = scheduler.current_subreddit(context, chat_id)

    if not scheduler.stop_monitoring(context, chat_id):
        await update.message.reply_text(format_not_subscribed(), parse_mode="Markdown")
        return

    await update.message.reply_text(
        format_unsubscribe_success(current or "the subreddit"), parse_mode="Markdown"
    )


# ── Application bootstrap ──────────────────────────────────────────────────────

def main() -> None:
    """Build the Application, register handlers, and start polling."""
    logger.info("Starting Reddit Monitor Bot…")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("top", top_handler))
    app.add_handler(CommandHandler("subscribe", subscribe_handler))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))

    logger.info(
        "Bot is running. Check interval: %ss. Press Ctrl+C to stop.",
        config.CHECK_INTERVAL,
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
