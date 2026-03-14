# Reddit Monitor Bot 🤖

A Telegram bot that monitors subreddits and delivers instant alerts when new posts appear — built with Python, python-telegram-bot, and the Reddit public JSON API.

> **Portfolio project** demonstrating Python automation, REST API integration, async programming, and Telegram bot development.

---

## Features

- 📌 **Top posts** — Fetch the top 5 posts of the day from any public subreddit
- 🔔 **Live monitoring** — Subscribe to a subreddit and get alerted the moment a new post appears
- ✅ **Clean alerts** — Professional Telegram messages with bold titles, inline links, and score indicators
- ❌ **Graceful errors** — User-friendly messages for invalid subreddits, API failures, and missing arguments
- ⚡ **Async** — Fully async with python-telegram-bot v21 and APScheduler job queue

---

## Tech Stack

| Layer | Library |
|---|---|
| Telegram bot | `python-telegram-bot` v21 |
| HTTP requests | `requests` |
| Environment config | `python-dotenv` |
| Scheduling | `APScheduler` (bundled with PTB job-queue extra) |

---

## Project Structure

```
telegram-reddit-monitor-bot/
├── bot.py              # Entry point — handlers and app bootstrap
├── reddit_service.py   # Reddit API calls (get_top_posts, get_newest_post)
├── scheduler.py        # JobQueue logic — start/stop monitoring per chat
├── formatting.py       # All Telegram message templates
├── config.py           # Environment variable loading and validation
├── requirements.txt    # Pinned dependencies
├── .env.example        # Template for your .env file
├── README.md
└── screenshots/        # Portfolio screenshots (add yours here)
```

---

## Want this bot for your community?

I can set this up for your subreddit, Telegram group, or any custom use case.

👉 **[Order on Fiverr](https://www.fiverr.com/YOUR_GIG_URL)**

---

## Available Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Welcome message | `/start` |
| `/help` | List all commands | `/help` |
| `/top <subreddit>` | Top 5 posts of the day | `/top worldnews` |
| `/subscribe <subreddit>` | Monitor a subreddit for new posts | `/subscribe programming` |
| `/unsubscribe` | Stop monitoring | `/unsubscribe` |

### Notes

- Subreddit names are case-insensitive: `/top Python` and `/top python` both work
- The `r/` prefix is optional: `/subscribe r/python` and `/subscribe python` both work
- Only one subscription is active at a time per user — subscribing to a new subreddit replaces the old one

---

## How Monitoring Works

1. You send `/subscribe <subreddit>`
2. The bot validates the subreddit exists
3. A background job starts, polling `reddit.com/r/{subreddit}/new.json` every `CHECK_INTERVAL` seconds
4. On the first check, it silently records the current latest post ID
5. On every subsequent check, if the newest post ID has changed, it sends you an alert
6. Use `/unsubscribe` to cancel

---

## Screenshots

_Add your portfolio screenshots here._

| Command | Screenshot |
|---|---|
| `/start` | _(add screenshot)_ |
| `/help` | _(add screenshot)_ |
| `/top python` | _(add screenshot)_ |
| `/subscribe python` | _(add screenshot)_ |
| Live alert | _(add screenshot)_ |
| Error — bad subreddit | _(add screenshot)_ |

---

## License

MIT — free to use, modify, and distribute.
