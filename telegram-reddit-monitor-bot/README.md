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

## Installation

### 1. Prerequisites

- Python 3.11 or higher
- A Telegram account
- Git (optional)

### 2. Clone the repository

```bash
git clone https://github.com/yourusername/telegram-reddit-monitor-bot.git
cd telegram-reddit-monitor-bot
```

### 3. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a **name** (e.g. `Reddit Monitor`)
4. Choose a **username** ending in `bot` (e.g. `my_reddit_monitor_bot`)
5. BotFather will reply with your **bot token** — copy it, you'll need it next

---

## Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ   # from BotFather
CHECK_INTERVAL=180                                          # seconds between checks (180 = 3 min)
```

---

## Running the Bot

```bash
python bot.py
```

You should see:

```
2026-01-01 12:00:00 | INFO     | __main__ — Starting Reddit Monitor Bot…
2026-01-01 12:00:01 | INFO     | __main__ — Bot is running. Check interval: 180s. Press Ctrl+C to stop.
```

Open Telegram, find your bot, and send `/start`.

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
