"""
ui.py — All Telegram UI: keyboards, message templates, formatters
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Buttons, Emoji, ADD_BOT_LINK, SUPPORT_GROUP, SUPPORT_CHANNEL


# ╔══════════════════════════════════════════════════════════════╗
# ║              CUSTOM EMOJI HELPER                             ║
# ╚══════════════════════════════════════════════════════════════╝

def ce(emoji_id: str, fallback: str = "⭐") -> str:
    """Render a Telegram custom emoji by ID."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# ── Shorthand references ─────────────────────────────────────────
E = Emoji   # E.COIN, E.FIRE etc.


# ╔══════════════════════════════════════════════════════════════╗
# ║                   KEYBOARDS                                  ║
# ╚══════════════════════════════════════════════════════════════╝

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{Buttons.ADD_BOT_TEXT}",
                url=ADD_BOT_LINK
            ),
        ],
        [
            InlineKeyboardButton(
                f"{Buttons.SUPPORT_GRP_TEXT}",
                url=SUPPORT_GROUP
            ),
            InlineKeyboardButton(
                f"{Buttons.SUPPORT_CH_TEXT}",
                url=SUPPORT_CHANNEL
            ),
        ],
        [
            InlineKeyboardButton(
                f"{Buttons.HELP_TEXT}",
                callback_data="help"
            ),
        ],
    ])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(Buttons.NEW_GAME_TEXT,   callback_data="new_game"),
            InlineKeyboardButton(Buttons.DAILY_TEXT,      callback_data="daily"),
        ],
        [
            InlineKeyboardButton(Buttons.BLITZ_TEXT,      callback_data="blitz"),
            InlineKeyboardButton(Buttons.LEADERBOARD_TEXT,callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton(Buttons.WALLET_TEXT,     callback_data="wallet"),
            InlineKeyboardButton(Buttons.SHOP_TEXT,       callback_data="shop"),
        ],
        [
            InlineKeyboardButton(Buttons.MARKET_TEXT,     callback_data="market"),
        ],
    ])


def game_keyboard(session_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💡 Hint (5 $WRD)",    callback_data=f"hint_{session_id}"),
            InlineKeyboardButton("🔄 Shuffle (12 $WRD)", callback_data=f"shuffle_{session_id}"),
        ],
        [
            InlineKeyboardButton("⏱ Freeze (8 $WRD)",  callback_data=f"freeze_{session_id}"),
            InlineKeyboardButton("🔓 +Letter (10 $WRD)",callback_data=f"letter_{session_id}"),
        ],
        [
            InlineKeyboardButton("🏁 End Game",          callback_data=f"endgame_{session_id}"),
        ],
    ])


def shop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(Buttons.BUY_HINT_TEXT,          callback_data="buy_hint")],
        [InlineKeyboardButton(Buttons.BUY_LETTER_TEXT,        callback_data="buy_letter")],
        [InlineKeyboardButton(Buttons.BUY_SHUFFLE_TEXT,       callback_data="buy_shuffle")],
        [InlineKeyboardButton(Buttons.BUY_TIME_FREEZE_TEXT,   callback_data="buy_freeze")],
        [InlineKeyboardButton(Buttons.BUY_STREAK_SHIELD_TEXT, callback_data="buy_shield")],
        [InlineKeyboardButton(Buttons.BUY_MYSTERY_BOX_TEXT,   callback_data="buy_mystery")],
        [
            InlineKeyboardButton("🎨 Themes",           callback_data="shop_cosmetics"),
            InlineKeyboardButton("🔙 Back",             callback_data="menu"),
        ],
    ])


def back_keyboard(cb: str = "menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=cb)]])


def confirm_keyboard(yes_cb: str, no_cb: str = "menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirm", callback_data=yes_cb),
        InlineKeyboardButton("❌ Cancel",  callback_data=no_cb),
    ]])


def cosmetics_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏷 Custom Title — 100 $WRD",  callback_data="buy_title")],
        [InlineKeyboardButton("🎨 Profile Theme — 80 $WRD",  callback_data="buy_theme")],
        [InlineKeyboardButton("😎 Avatar Frame — 120 $WRD",  callback_data="buy_frame")],
        [InlineKeyboardButton("🔙 Back to Shop",             callback_data="shop")],
    ])


# ╔══════════════════════════════════════════════════════════════╗
# ║                  MESSAGE TEMPLATES                           ║
# ╚══════════════════════════════════════════════════════════════╝

def start_msg(full_name: str) -> str:
    return (
        f"<blockquote>"
        f"🎉 Welcome to <b>Wordly Bot</b>, {full_name}! "
        f"{ce(E.BRAIN,'🧠')}{ce(E.SPARKLE,'✨')}\n"
        f"</blockquote>\n\n"
        f"{ce(E.LETTERS,'🔤')} <b>Build words. Earn $WRD. Rule the board.</b>\n\n"
        f"<blockquote expandable>"
        f"🎮 /new — Start a game\n"
        f"📖 /help — Commands & rules\n"
        f"👛 /wallet — Your coin balance\n"
        f"🏪 /shop — Spend your $WRD\n"
        f"🏆 /top — Leaderboard\n"
        f"📊 /market — $WRD economy stats"
        f"</blockquote>"
    )


def help_msg() -> str:
    return (
        f"<blockquote>📖 <b>How to Play Wordly</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.GAME,'🎮')} Send /new to start a round.\n"
        f"{ce(E.LETTERS,'🔤')} Create valid English words using the given letters.\n"
        f"{ce(E.INFO,'ℹ️')} Words must be <b>3 to 12 letters</b> long.\n"
        f"{ce(E.SUCCESS,'✅')} Letter repetition is <b>completely allowed!</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.COIN,'🪙')} <b>Points & $WRD System</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>"
        f"🔸 3 letters → <b>1 pt + 1 $WRD</b>\n"
        f"🔸 4 letters → <b>2 pts + 2 $WRD</b>\n"
        f"🔸 5 letters → <b>4 pts + 4 $WRD</b>\n"
        f"🔸 6 letters → <b>7 pts + 7 $WRD</b>\n"
        f"🔸 7 letters → <b>12 pts + 12 $WRD</b>\n"
        f"🎯 8–12 letters → <b>20 pts + 20 $WRD</b> (MAX!)"
        f"</blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.FIRE,'🔥')} <b>Streak Bonuses</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>"
        f"3-day streak → +15 $WRD\n"
        f"7-day streak → +50 $WRD\n"
        f"Daily challenge → +25 $WRD"
        f"</blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.GAME,'🎮')} <b>Commands</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>"
        f"/new — Normal game (2 min)\n"
        f"/blitz — Speed round (60 sec)\n"
        f"/daily — Daily challenge\n"
        f"/wallet — Coin balance\n"
        f"/shop — Buy power-ups\n"
        f"/market — $WRD economy\n"
        f"/top — Leaderboard\n"
        f"/streak — Your streak\n"
        f"/profile — Your stats\n"
        f"/menu — Main menu"
        f"</blockquote>"
    )


def game_start_msg(letters: list, mode: str, time_left: int) -> str:
    letter_display = "  ".join([f"<b>{l}</b>" for l in letters])
    mode_label = {"normal": "📝 Normal", "blitz": "⚡ Blitz", "daily": "📅 Daily Challenge"}.get(mode, mode)
    return (
        f"<blockquote>{ce(E.GAME,'🎮')} <b>{mode_label} — Game On!</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.LETTERS,'🔤')} <b>Your Letters:</b>\n\n"
        f"┌─────────────────┐\n"
        f"│  {letter_display}  │\n"
        f"└─────────────────┘\n\n"
        f"⏱ Time: <b>{time_left}s</b>  |  "
        f"{ce(E.COIN,'🪙')} Score: <b>0</b>  |  Words: <b>0</b>\n\n"
        f"<blockquote expandable>"
        f"💬 Just type any word to submit!\n"
        f"🔁 Letters can be reused freely.\n"
        f"💡 Use buttons below for power-ups."
        f"</blockquote>"
    )


def word_accepted_msg(result: dict, letters: list) -> str:
    letter_display = "  ".join([f"<b>{l}</b>" for l in letters])
    return (
        f"{ce(E.SUCCESS,'✅')} <b>+{result['points']} pts</b>  "
        f"{ce(E.COIN,'🪙')} <b>+{result['coins']} $WRD</b>  "
        f"— <code>{result['word']}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.LETTERS,'🔤')} <b>Letters:</b>  {letter_display}\n\n"
        f"📊 Score: <b>{result['total_score']}</b>  │  "
        f"{ce(E.COIN,'🪙')} <b>{result['total_coins']} $WRD</b>  │  "
        f"Words: <b>{result['words_found']}</b>"
    )


def game_over_msg(summary: dict, pb_bonus: int, streak_info: dict, new_balance: int) -> str:
    pb_line = f"\n{ce(E.TROPHY,'🏆')} <b>New Personal Best!</b> +{pb_bonus} $WRD bonus!" if pb_bonus else ""
    streak_line = ""
    if streak_info.get("bonus"):
        streak_line = f"\n{ce(E.FIRE,'🔥')} <b>{streak_info['streak']}-day streak!</b> +{streak_info['bonus']} $WRD"
    return (
        f"<blockquote>{ce(E.PARTY,'🎉')} <b>Game Over!</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 Final Score:  <b>{summary['score']} pts</b>\n"
        f"{ce(E.COIN,'🪙')} Earned:  <b>{summary['coins_earned']} $WRD</b>\n"
        f"📝 Words Found:  <b>{summary['word_count']}</b>\n"
        f"⏱ Duration:  <b>{summary['duration']}s</b>{pb_line}{streak_line}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>"
        f"{ce(E.WALLET,'👛')} Your Balance: <b>{new_balance} $WRD</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔁 /new — Play again   🏪 /shop — Spend coins"
        f"</blockquote>"
    )


def wallet_msg(user: dict) -> str:
    inv = user.get("inventory", {})
    inv_lines = ""
    if inv.get("streak_shield"):  inv_lines += "🛡 Streak Shield (active)\n"
    if inv.get("time_freeze"):    inv_lines += "⏱ Time Freeze (ready)\n"
    if not inv_lines: inv_lines = "Empty — visit /shop!\n"
    return (
        f"<blockquote>{ce(E.WALLET,'👛')} <b>Your $WRD Wallet</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.COIN,'🪙')} <b>Balance:</b>  <code>{user['coins']} $WRD</code>\n\n"
        f"📊 <b>Stats</b>\n"
        f"<blockquote>"
        f"🏆 Total Score:   <b>{user.get('total_score',0)}</b>\n"
        f"🎮 Games Played:  <b>{user.get('games_played',0)}</b>\n"
        f"📝 Words Found:   <b>{user.get('words_found',0)}</b>\n"
        f"🔥 Streak:        <b>{user.get('streak',0)} days</b>\n"
        f"⭐ Rank:          <b>{user.get('rank','Beginner')}</b>\n"
        f"🥇 Personal Best: <b>{user.get('personal_best',0)} pts</b>"
        f"</blockquote>\n\n"
        f"🎒 <b>Inventory</b>\n"
        f"<blockquote>{inv_lines}</blockquote>"
    )


def shop_msg(coins: int) -> str:
    return (
        f"<blockquote>{ce(E.SHOP,'🏪')} <b>$WRD Shop</b></blockquote>\n\n"
        f"{ce(E.COIN,'🪙')} Your Balance: <b>{coins} $WRD</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Power-Ups</b>\n"
        f"<blockquote>"
        f"💡 Hint             — <b>5 $WRD</b>\n"
        f"🔓 Letter Unlock    — <b>10 $WRD</b>\n"
        f"⏱ Time Freeze      — <b>8 $WRD</b>\n"
        f"🔄 Shuffle Letters  — <b>12 $WRD</b>\n"
        f"🛡 Streak Shield    — <b>40 $WRD</b>\n"
        f"📦 Mystery Box      — <b>20 $WRD</b>"
        f"</blockquote>\n\n"
        f"🎨 <b>Cosmetics</b>\n"
        f"<blockquote>"
        f"🏷 Custom Title     — <b>100 $WRD</b>\n"
        f"🎨 Profile Theme    — <b>80 $WRD</b>\n"
        f"😎 Avatar Frame     — <b>120 $WRD</b>"
        f"</blockquote>"
    )


def market_msg(stats: dict) -> str:
    burn_rate = stats.get("total_coins_spent", 0)
    earned    = stats.get("total_coins_earned", 0)
    supply    = stats.get("circulating_supply", 0)
    inflation = "📈 Rising" if earned > burn_rate * 1.2 else ("📉 Deflating" if burn_rate > earned else "⚖️ Stable")
    return (
        f"<blockquote>{ce(E.CHART_UP,'📊')} <b>$WRD Market Dashboard</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💹 <b>Live Economy</b>\n"
        f"<blockquote>"
        f"🪙 Circulating Supply:  <b>{supply:,} $WRD</b>\n"
        f"📈 Total Earned:         <b>{earned:,} $WRD</b>\n"
        f"📉 Total Burned (spent): <b>{burn_rate:,} $WRD</b>\n"
        f"📊 Market Pressure:      <b>{inflation}</b>"
        f"</blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Network Stats</b>\n"
        f"<blockquote>"
        f"👥 Total Players:   <b>{stats.get('total_users',0):,}</b>\n"
        f"🎮 Total Games:     <b>{stats.get('total_games',0):,}</b>\n"
        f"⚡ Active Today:    <b>{stats.get('today_active',0):,}</b>\n"
        f"🎯 Games Today:     <b>{stats.get('today_games',0):,}</b>"
        f"</blockquote>\n\n"
        f"<blockquote expandable>"
        f"📌 $WRD is the native currency of Wordly Bot.\n"
        f"Earn by playing. Spend in /shop.\n"
        f"Symbol: $WRD  |  Backed by: Your vocabulary 📚"
        f"</blockquote>"
    )


def leaderboard_msg(entries: list, rich_list: list) -> str:
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lb = ""
    for i, u in enumerate(entries):
        name = u.get("full_name", "Unknown")[:20]
        lb += f"{medals[i]} <b>{name}</b>  —  {u['total_score']} pts  {ce(E.COIN,'🪙')}{u['coins']}\n"
    rl = ""
    for u in rich_list:
        name = u.get("full_name", "Unknown")[:15]
        rl += f"  {ce(E.COIN,'🪙')} <b>{name}</b>  —  {u['coins']} $WRD\n"
    return (
        f"<blockquote>{ce(E.TROPHY,'🏆')} <b>Leaderboard</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Top Scorers</b>\n"
        f"<blockquote>{lb}</blockquote>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.COIN,'🪙')} <b>$WRD Rich List</b>\n"
        f"<blockquote>{rl}</blockquote>"
    )


def owner_stats_msg(stats: dict) -> str:
    return (
        f"<blockquote>{ce(E.CROWN,'👑')} <b>Owner Dashboard</b></blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Users</b>\n"
        f"<blockquote>"
        f"Total Registered:  <b>{stats.get('total_registered',0):,}</b>\n"
        f"New Today:         <b>{stats.get('new_today',0):,}</b>\n"
        f"Active Today:      <b>{stats.get('today_active',0):,}</b>\n"
        f"Banned:            <b>{stats.get('banned_users',0)}</b>"
        f"</blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎮 <b>Gameplay</b>\n"
        f"<blockquote>"
        f"Total Games:       <b>{stats.get('total_games',0):,}</b>\n"
        f"Games Today:       <b>{stats.get('today_games',0):,}</b>"
        f"</blockquote>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{ce(E.COIN,'🪙')} <b>Economy</b>\n"
        f"<blockquote>"
        f"Coins Earned:      <b>{stats.get('total_coins_earned',0):,} $WRD</b>\n"
        f"Coins Spent:       <b>{stats.get('total_coins_spent',0):,} $WRD</b>\n"
        f"Circulating:       <b>{stats.get('circulating_supply',0):,} $WRD</b>"
        f"</blockquote>"
    )
