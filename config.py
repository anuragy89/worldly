# ╔══════════════════════════════════════════════════════════════╗
# ║              WORDLY BOT — MASTER CONFIG                      ║
# ║         Change everything from here. One place. Done.        ║
# ╚══════════════════════════════════════════════════════════════╝

import os

# ─── BOT CREDENTIALS ────────────────────────────────────────────
BOT_TOKEN        = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OWNER_ID         = int(os.getenv("OWNER_ID", "123456789"))       # Your Telegram user ID
MONGO_URI        = os.getenv("MONGO_URI", "mongodb+srv://...")   # MongoDB Atlas URI
DB_NAME          = os.getenv("DB_NAME", "wordly_bot")

# ─── BOT LINKS ──────────────────────────────────────────────────
BOT_USERNAME     = os.getenv("BOT_USERNAME", "YourWordlyBot")
SUPPORT_GROUP    = os.getenv("SUPPORT_GROUP", "https://t.me/your_support_group")
SUPPORT_CHANNEL  = os.getenv("SUPPORT_CHANNEL", "https://t.me/your_channel")
ADD_BOT_LINK     = os.getenv("ADD_BOT_LINK", "https://t.me/YourWordlyBot?startgroup=true")

# ─── WELCOME IMAGE ──────────────────────────────────────────────
# Drop your welcome image URL here (rendered above start message)
WELCOME_IMAGE_URL = os.getenv(
    "WELCOME_IMAGE_URL",
    "https://ibb.co/twL7H06z"   # ← replace with your image
)

# ╔══════════════════════════════════════════════════════════════╗
# ║                  PREMIUM EMOJI IDs                           ║
# ║  Get ID: forward any custom emoji msg → @getidsbot          ║
# ║  Format: CustomEmoji(id=XXXXXXXXXX)                         ║
# ╚══════════════════════════════════════════════════════════════╝

class Emoji:
    # ── Coin / Economy ──────────────────────────────────────────
    COIN          = os.getenv("EMOJI_COIN",    "5368324170671202286")   # 🪙
    WALLET        = os.getenv("EMOJI_WALLET",  "5372981976804366741")   # 👛
    CHART_UP      = os.getenv("EMOJI_CHART_UP","5373026167722876724")   # 📈
    CHART_DOWN    = os.getenv("EMOJI_CHART_DN","5372969420424743478")   # 📉
    SHOP          = os.getenv("EMOJI_SHOP",    "5373141891321001152")   # 🏪
    DIAMOND       = os.getenv("EMOJI_DIAMOND", "5368324170671202111")   # 💎
    FIRE          = os.getenv("EMOJI_FIRE",    "5368324170671202333")   # 🔥
    GIFT          = os.getenv("EMOJI_GIFT",    "5372962828756564177")   # 🎁
    MYSTERY       = os.getenv("EMOJI_MYSTERY", "5373141891321001999")   # 📦

    # ── Game ────────────────────────────────────────────────────
    GAME          = os.getenv("EMOJI_GAME",    "5373026167722876000")   # 🎮
    TROPHY        = os.getenv("EMOJI_TROPHY",  "5368324170671202444")   # 🏆
    STAR          = os.getenv("EMOJI_STAR",    "5368324170671202555")   # ⭐
    LIGHTNING     = os.getenv("EMOJI_BOLT",    "5368324170671202666")   # ⚡
    TIMER         = os.getenv("EMOJI_TIMER",   "5368324170671202777")   # ⏱
    HINT          = os.getenv("EMOJI_HINT",    "5368324170671202888")   # 💡
    SHIELD        = os.getenv("EMOJI_SHIELD",  "5368324170671202999")   # 🛡
    DICE          = os.getenv("EMOJI_DICE",    "5368324170671203000")   # 🎲
    LETTERS       = os.getenv("EMOJI_LETTERS", "5368324170671203111")   # 🔤
    BRAIN         = os.getenv("EMOJI_BRAIN",   "5368324170671203222")   # 🧠

    # ── Status ──────────────────────────────────────────────────
    SUCCESS       = os.getenv("EMOJI_OK",      "5368324170671203333")   # ✅
    ERROR         = os.getenv("EMOJI_ERR",     "5368324170671203444")   # ❌
    INFO          = os.getenv("EMOJI_INFO",    "5368324170671203555")   # ℹ️
    CROWN         = os.getenv("EMOJI_CROWN",   "5368324170671203666")   # 👑
    ROCKET        = os.getenv("EMOJI_ROCKET",  "5368324170671203777")   # 🚀
    SPARKLE       = os.getenv("EMOJI_SPARKLE", "5368324170671203888")   # ✨
    PARTY         = os.getenv("EMOJI_PARTY",   "5368324170671203999")   # 🎉
    STREAK        = os.getenv("EMOJI_STREAK",  "5368324170671204000")   # 🔥 (streak specific)
    LOCK          = os.getenv("EMOJI_LOCK",    "5368324170671204111")   # 🔒

# ╔══════════════════════════════════════════════════════════════╗
# ║               COLOURED BUTTON TEXTS                          ║
# ║   Only 3 colours allowed: RED 🔴  GREEN 🟢  BLUE 🔵         ║
# ╚══════════════════════════════════════════════════════════════╝

class Buttons:
    # ── Start Screen ────────────────────────────────────────────
    ADD_BOT_TEXT      = "➕ Add to Group"        # GREEN
    SUPPORT_GRP_TEXT  = "💬 Support Group"       # BLUE
    SUPPORT_CH_TEXT   = "📢 Channel"             # BLUE
    HELP_TEXT         = "📖 Help & Commands"     # RED

    # ── Game Screen ─────────────────────────────────────────────
    NEW_GAME_TEXT     = "🎮 New Game"            # GREEN
    DAILY_TEXT        = "📅 Daily Challenge"     # BLUE
    BLITZ_TEXT        = "⚡ Blitz Mode"          # RED

    # ── Economy Screen ──────────────────────────────────────────
    WALLET_TEXT       = "👛 My Wallet"           # BLUE
    SHOP_TEXT         = "🏪 Shop"               # GREEN
    MARKET_TEXT       = "📊 $WRD Market"         # BLUE
    LEADERBOARD_TEXT  = "🏆 Leaderboard"         # RED

    # ── Shop Items ──────────────────────────────────────────────
    BUY_HINT_TEXT         = "💡 Buy Hint — 5 $WRD"
    BUY_LETTER_TEXT       = "🔓 Letter Unlock — 10 $WRD"
    BUY_SHUFFLE_TEXT      = "🔄 Shuffle Letters — 12 $WRD"
    BUY_STREAK_SHIELD_TEXT= "🛡 Streak Shield — 40 $WRD"
    BUY_MYSTERY_BOX_TEXT  = "📦 Mystery Box — 20 $WRD"
    BUY_TIME_FREEZE_TEXT  = "⏱ Time Freeze — 8 $WRD"

# ╔══════════════════════════════════════════════════════════════╗
# ║                    GAME SETTINGS                             ║
# ╚══════════════════════════════════════════════════════════════╝

class GameSettings:
    MIN_WORD_LEN        = 3
    MAX_WORD_LEN        = 12
    LETTERS_COUNT       = 7           # letters given per round
    ROUND_DURATION      = 120         # seconds per normal round
    BLITZ_DURATION      = 60          # seconds for blitz mode
    DAILY_BONUS         = 25          # $WRD for daily challenge
    STREAK_3_BONUS      = 15
    STREAK_7_BONUS      = 50
    FIRST_GAME_BONUS    = 10
    REFER_BONUS         = 30
    PB_BONUS            = 20

    # Score → $WRD multiplier (word_length: wrd_earned)
    WORD_REWARDS = {
        3: 1,  4: 2,  5: 4,
        6: 7,  7: 12, 8: 20
    }

    # Score points (same keys)
    WORD_POINTS = {
        3: 1,  4: 2,  5: 4,
        6: 7,  7: 12, 8: 20
    }

# ╔══════════════════════════════════════════════════════════════╗
# ║                    SHOP PRICES ($WRD)                        ║
# ╚══════════════════════════════════════════════════════════════╝

class ShopPrices:
    HINT            = 5
    LETTER_UNLOCK   = 10
    TIME_FREEZE     = 8
    SHUFFLE         = 12
    STREAK_SHIELD   = 40
    MYSTERY_BOX     = 20
    CUSTOM_TITLE    = 100
    PROFILE_THEME   = 80
    AVATAR_FRAME    = 120
    TOURNAMENT_ENTRY= 50

    MYSTERY_BOX_MIN = 10
    MYSTERY_BOX_MAX = 200

# ─── DICTIONARY API ─────────────────────────────────────────────
DICT_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

# ─── HEROKU / WEBHOOK ───────────────────────────────────────────
WEBHOOK_URL  = os.getenv("WEBHOOK_URL", "")    # e.g. https://yourapp.herokuapp.com
PORT         = int(os.getenv("PORT", 8443))
USE_WEBHOOK  = os.getenv("USE_WEBHOOK", "true").lower() == "true"
