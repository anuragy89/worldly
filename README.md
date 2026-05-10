# 🎉 Wordly Bot — Complete Deployment Guide

## 📁 Project Structure
```
wordly_bot/
├── bot.py            # Main bot handlers
├── config.py         # ⭐ ALL settings in one place
├── database.py       # MongoDB operations
├── game_engine.py    # Word game logic
├── ui.py             # Messages & keyboards
├── requirements.txt  # Python deps
├── Dockerfile        # Heroku container
├── Procfile          # Heroku process
└── app.json          # Heroku one-click config
```

---

## 🚀 Quick Deploy to Heroku

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/anuragy89/wordly)


## ⚙️ Step 1 — Configure `config.py`

Open `config.py` and fill in:

```python
BOT_TOKEN    = "YOUR_BOT_TOKEN"       # from @BotFather
OWNER_ID     = 123456789              # your Telegram ID (from @userinfobot)
MONGO_URI    = "mongodb+srv://..."    # MongoDB Atlas URI
SUPPORT_GROUP   = "https://t.me/..."
SUPPORT_CHANNEL = "https://t.me/..."
WELCOME_IMAGE_URL = "https://..."    # Your banner image URL
```

---

## 🎨 Step 2 — Set Premium Emoji IDs

In `config.py` → `class Emoji`, replace each emoji ID:

```python
# How to get emoji IDs:
# 1. Send a message with your custom emoji to any chat
# 2. Forward it to @getidsbot
# 3. Copy the emoji ID (looks like: 5368324170671202286)
# 4. Paste into the matching field in class Emoji

COIN   = "5368324170671202286"   # your coin emoji ID
FIRE   = "5368324170671202333"   # your fire emoji ID
# ... etc
```

All emojis are used as environment variables too:
```bash
heroku config:set EMOJI_COIN=5368324170671202286
```

---

## 🗄️ Step 3 — MongoDB Setup

1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) → Create free cluster
2. Create database user → Get connection string
3. Paste URI into `MONGO_URI` in `config.py` or Heroku env vars

---

## 🚀 Step 4 — Deploy to Heroku (Docker, 2x Standard)

### One-time setup:
```bash
# Install Heroku CLI, then:
heroku login
heroku create your-wordly-bot
heroku stack:set container -a your-wordly-bot

# Set environment variables
heroku config:set BOT_TOKEN=your_token -a your-wordly-bot
heroku config:set OWNER_ID=your_id -a your-wordly-bot
heroku config:set MONGO_URI="mongodb+srv://..." -a your-wordly-bot
heroku config:set WEBHOOK_URL="https://your-wordly-bot.herokuapp.com" -a your-wordly-bot
heroku config:set USE_WEBHOOK=true -a your-wordly-bot
heroku config:set BOT_USERNAME=YourBotUsername -a your-wordly-bot
heroku config:set DB_NAME=wordly_bot -a your-wordly-bot
heroku config:set SUPPORT_GROUP=https://t.me/yourgroup -a your-wordly-bot
heroku config:set SUPPORT_CHANNEL=https://t.me/yourchannel -a your-wordly-bot
heroku config:set ADD_BOT_LINK="https://t.me/YourBot?startgroup=true" -a your-wordly-bot
heroku config:set WELCOME_IMAGE_URL=https://your-image-url.com/img.jpg -a your-wordly-bot
```

### Scale to 2x Standard:
```bash
heroku ps:resize web=standard-2x -a your-wordly-bot
```

### Deploy:
```bash
git init
git add .
git commit -m "Initial deploy"
heroku git:remote -a your-wordly-bot
git push heroku main
```

### Check logs:
```bash
heroku logs --tail -a your-wordly-bot
```

---

## 👑 Owner Commands

| Command | Description |
|---|---|
| `/stats` | Full bot growth dashboard |
| `/broadcast <msg>` | Send message to ALL users |
| `/ban <user_id>` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/addcoins <id> <amount>` | Give $WRD to a user |

---

## 🎮 Player Commands

| Command | Description |
|---|---|
| `/start` | Welcome screen |
| `/new` | Normal game (2 min) |
| `/blitz` | Speed round (60 sec) |
| `/daily` | Daily challenge (+25 $WRD) |
| `/wallet` | Coin balance & stats |
| `/shop` | Buy power-ups |
| `/market` | $WRD economy dashboard |
| `/top` | Leaderboard |
| `/streak` | Streak tracker |
| `/profile` | Full profile |
| `/menu` | Main menu |

---

## 🪙 $WRD Economy

**Earn:** Play games, daily challenge, streaks, referrals, personal bests

**Spend:** Hints (5), Letter Unlock (10), Time Freeze (8), Shuffle (12), Streak Shield (40), Mystery Box (20), Cosmetics (80–120)

---

## 🔧 Quick Customization

| What to change | Where |
|---|---|
| All emoji IDs | `config.py → class Emoji` |
| Button texts | `config.py → class Buttons` |
| Game duration, word length | `config.py → class GameSettings` |
| Shop prices | `config.py → class ShopPrices` |
| Bot links | `config.py` top section |
| Welcome image | `config.py → WELCOME_IMAGE_URL` |
