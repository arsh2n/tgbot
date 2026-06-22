# Proxy Shop Telegram Bot

A Telegram bot for selling proxy packages with Paytm/UPI payment flow, deployable on Railway via GitHub.

---

## Features

- 18+ age gate with inline Yes/No buttons
- Catalogue image with A–J package buttons
- **A** → account balance check
- **B** → demo channel link
- **C–J** → Paytm/UPI QR code + payment confirmation flow
- Graceful fallback to support contact if no payment proof sent

---

## Project Structure

```
├── bot.py            ← main bot
├── requirements.txt
├── Procfile
├── railway.toml
├── .env.example      ← copy to .env for local dev
└── README.md
```

---

## Step 1 — Create your Telegram bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the **BOT_TOKEN** you receive

---

## Step 2 — Get Telegram file IDs for your images

The fastest way to serve images is by Telegram file_id (instead of a URL).

1. Start your bot (even before full setup)
2. Send your **catalogue image** and your **QR code image** to [@userinfobot](https://t.me/userinfobot) or just forward them to your bot and grab the file_id from the logs
3. Alternatively, use any public HTTPS image URL

---

## Step 3 — Deploy to Railway

### 3a. Push to GitHub

```bash
git init
git add .
git commit -m "init proxy bot"
gh repo create proxy-bot --private --push --source=.
# or push manually to an existing GitHub repo
```

### 3b. Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**
2. Select your repo

### 3c. Set environment variables

In Railway → your service → **Variables**, add:

| Variable | Value |
|---|---|
| `BOT_TOKEN` | `123456789:ABCxxx` |
| `CATALOGUE_PHOTO` | Telegram file_id or HTTPS URL |
| `QR_CODE_PHOTO` | Telegram file_id or HTTPS URL |
| `DEMO_CHANNEL` | `https://t.me/your_demo_channel` |
| `SUPPORT` | `@yoursupporthandle` |
| `WEBHOOK_URL` | *(leave blank for now — fill in step 3d)* |

### 3d. Set WEBHOOK_URL after first deploy

1. After Railway deploys, copy the generated domain (e.g. `https://myproxybot.up.railway.app`)
2. Add it as `WEBHOOK_URL` in Variables
3. Railway will auto-redeploy

---

## Local Development

```bash
pip install -r requirements.txt
cp .env.example .env      # fill in your values (leave WEBHOOK_URL blank)
python bot.py             # runs in polling mode locally
```

---

## Customising Package Names

Edit `OPTION_NAMES` in `bot.py` to label your packages:

```python
OPTION_NAMES = {
    "A": "Check Balance",
    "B": "Demo Channel",
    "C": "Starter Pack – 10 Proxies",
    "D": "Basic Pack – 25 Proxies",
    "E": "Standard Pack – 50 Proxies",
    "F": "Pro Pack – 100 Proxies",
    ...
}
```

---

## Notes

- Railway sets `PORT` automatically — don't override it
- Without `CATALOGUE_PHOTO` / `QR_CODE_PHOTO` set, the bot falls back to text messages so it always works
- Each user's conversation state is tracked independently (`per_user=True`)
- `/cancel` resets a session at any point
