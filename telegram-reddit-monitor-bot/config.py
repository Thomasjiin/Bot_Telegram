"""
config.py — Centralised configuration loaded from environment variables.

All settings are validated at import time so the bot fails fast with a
clear error message rather than silently misbehaving.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Return the value of a required environment variable or raise."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {key}\n"
            "Copy .env.example to .env and fill in your values."
        )
    return value


def _int_env(key: str, default: int) -> int:
    """Return an integer environment variable, with a clear error on bad values."""
    raw = os.getenv(key, str(default))
    try:
        return int(raw)
    except ValueError:
        raise EnvironmentError(
            f"Environment variable {key} must be an integer, got: {raw!r}"
        )


# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")

# ── Reddit ────────────────────────────────────────────────────────────────────
# Custom User-Agent is required by Reddit's API rules. Using a generic UA
# (e.g. "python-requests") often triggers rate-limiting (HTTP 429).
REDDIT_USER_AGENT: str = "script:telegram-reddit-bot:v1.0 (by /u/yourname)"

# ── Scheduler ─────────────────────────────────────────────────────────────────
# How often (in seconds) the job checks for new posts. Default: 3 minutes.
CHECK_INTERVAL: int = _int_env("CHECK_INTERVAL", 180)

# ── Reddit endpoints ──────────────────────────────────────────────────────────
REDDIT_TOP_URL: str = "https://www.reddit.com/r/{subreddit}/top.json?t=day&limit=5"
REDDIT_NEW_URL: str = "https://www.reddit.com/r/{subreddit}/new.json?limit=1"
