"""
bot.py — Main Wordly Bot handlers
"""

import asyncio
import logging
import random
import os

from telegram import Update, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

import database as db
import game_engine as ge
from config import (
    BOT_TOKEN, OWNER_ID, WELCOME_IMAGE_URL,
    GameSettings, ShopPrices, USE_WEBHOOK, WEBHOOK_URL, PORT
)
from ui import (
    start_msg, help_msg, game_start_msg, word_accepted_msg,
    game_over_msg, wallet_msg, shop_msg, market_msg,
    leaderboard_msg, owner_stats_msg,
    start_keyboard, main_menu_keyboard, game_keyboard,
    shop_keyboard, back_keyboard, confirm_keyboard,
    cosmetics_keyboard, ce, E
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────

async def ensure_user(update: Update) -> dict:
    u = update.effective_user
    return await db.upsert_user(u.id, u.username or "", u.full_name)


def owner_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("⛔ Owner only command.")
            return
        return await func(update, ctx)
    wrapper.__name__ = func.__name__
    return wrapper


async def safe_reply(update: Update, text: str, **kwargs):
    try:
        await update.effective_message.reply_text(
            text, parse_mode=ParseMode.HTML, **kwargs
        )
    except Exception as e:
        log.warning(f"safe_reply error: {e}")


# ╔══════════════════════════════════════════════════════════════╗
# ║                     COMMANDS                                 ║
# ╚══════════════════════════════════════════════════════════════╝

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    if user.get("banned"):
        await safe_reply(update, "⛔ You are banned from Wordly Bot.")
        return
    text = start_msg(update.effective_user.first_name)
    try:
        await update.message.reply_photo(
            photo=WELCOME_IMAGE_URL,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=start_keyboard()
        )
    except Exception:
        await safe_reply(update, text, reply_markup=start_keyboard())


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ensure_user(update)
    await safe_reply(update, help_msg(), reply_markup=back_keyboard("menu"))


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ensure_user(update)
    await safe_reply(
        update,
        f"<blockquote>🎮 <b>Wordly Main Menu</b></blockquote>\n\nChoose an action:",
        reply_markup=main_menu_keyboard()
    )


async def _start_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE, mode: str):
    user = await ensure_user(update)
    if user.get("banned"):
        await safe_reply(update, "⛔ You are banned.")
        return

    # Daily challenge check
    if mode == "daily":
        claimed = await db.claim_daily(user["user_id"])
        if not claimed:
            await safe_reply(
                update,
                f"<blockquote>📅 <b>Daily Challenge</b></blockquote>\n\n"
                f"✅ You've already done today's challenge!\n"
                f"Come back tomorrow for a fresh one. {ce(E.FIRE,'🔥')}",
                reply_markup=back_keyboard("menu")
            )
            return

    if ge.has_active_session(user["user_id"]):
        await safe_reply(
            update,
            f"⚠️ You already have an active game!\n"
            f"Type a word or press <b>🏁 End Game</b> first."
        )
        return

    sess = ge.create_session(user["user_id"], mode)
    msg_text = game_start_msg(sess.letters, mode, sess.time_left())
    msg = await safe_reply(update, msg_text, reply_markup=game_keyboard(sess.session_id))

    # Schedule auto-end when timer expires
    async def auto_end():
        duration = GameSettings.BLITZ_DURATION if mode == "blitz" else GameSettings.ROUND_DURATION
        await asyncio.sleep(duration + 2)
        active = ge.get_session(user["user_id"])
        if active and active.session_id == sess.session_id:
            await _finish_game(update, ctx, user["user_id"])

    asyncio.create_task(auto_end())


async def cmd_new(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _start_game(update, ctx, "normal")


async def cmd_blitz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _start_game(update, ctx, "blitz")


async def cmd_daily(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _start_game(update, ctx, "daily")


async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    await safe_reply(update, wallet_msg(user), reply_markup=back_keyboard("menu"))


async def cmd_shop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    await safe_reply(update, shop_msg(user["coins"]), reply_markup=shop_keyboard())


async def cmd_market(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats = await db.get_market_stats()
    await safe_reply(update, market_msg(stats), reply_markup=back_keyboard("menu"))


async def cmd_top(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    entries = await db.get_leaderboard(10)
    rich    = await db.get_coin_rich_list(5)
    await safe_reply(update, leaderboard_msg(entries, rich), reply_markup=back_keyboard("menu"))


async def cmd_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    await safe_reply(update, wallet_msg(user), reply_markup=back_keyboard("menu"))


async def cmd_streak(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    s = user.get("streak", 0)
    ms = user.get("max_streak", 0)
    shield = "🛡 <b>Streak Shield active</b> — one missed day is protected!\n" if user.get("streak_shield") else ""
    await safe_reply(
        update,
        f"<blockquote>{ce(E.FIRE,'🔥')} <b>Your Streak</b></blockquote>\n\n"
        f"🔥 Current Streak:  <b>{s} days</b>\n"
        f"🏆 Best Streak:     <b>{ms} days</b>\n"
        f"{shield}\n"
        f"<blockquote expandable>"
        f"Play every day to keep your streak!\n"
        f"3-day → +15 $WRD  |  7-day → +50 $WRD\n"
        f"Missing a day resets it to 0."
        f"</blockquote>",
        reply_markup=back_keyboard("menu")
    )


# ╔══════════════════════════════════════════════════════════════╗
# ║                   WORD SUBMISSION                            ║
# ╚══════════════════════════════════════════════════════════════╝

async def handle_word(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = await ensure_user(update)
    if user.get("banned"):
        return
    uid = user["user_id"]
    text = (update.message.text or "").strip()
    if not text or not text.isalpha():
        return

    sess = ge.get_session(uid)
    if not sess:
        return   # No active game — ignore silently

    if sess.is_expired():
        ge.end_session(uid)
        await _finish_game(update, ctx, uid, expired=True)
        return

    result = await sess.submit_word(text)
    if result["ok"]:
        await safe_reply(update, word_accepted_msg(result, sess.letters))
    else:
        await safe_reply(update, f"<blockquote>{result['reason']}</blockquote>")


async def _finish_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE,
                       uid: int, expired: bool = False):
    sess = ge.end_session(uid)
    if not sess:
        return
    summary   = sess.summary()
    pb_bonus  = await db.save_game(
        uid, summary["session_id"], summary["score"],
        summary["words"], summary["mode"],
        summary["coins_earned"], summary["duration"]
    )
    streak_info = await db.update_streak(uid)
    total_earn  = summary["coins_earned"] + pb_bonus + streak_info.get("bonus", 0)
    if total_earn > 0:
        await db.add_coins(uid, total_earn, "game_reward")
    # Daily bonus
    if summary["mode"] == "daily":
        await db.add_coins(uid, GameSettings.DAILY_BONUS, "daily_challenge")
        total_earn += GameSettings.DAILY_BONUS
    user = await db.get_user(uid)
    text = game_over_msg(summary, pb_bonus, streak_info, user["coins"])
    await safe_reply(update, text, reply_markup=main_menu_keyboard())


# ╔══════════════════════════════════════════════════════════════╗
# ║                  CALLBACK QUERIES                            ║
# ╚══════════════════════════════════════════════════════════════╝

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    data = q.data
    await q.answer()
    uid  = q.from_user.id
    user = await db.get_user(uid)
    if not user:
        user = await db.upsert_user(uid, q.from_user.username or "", q.from_user.full_name)

    async def edit(text, markup=None):
        try:
            await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
        except Exception:
            pass

    # ── Navigation ───────────────────────────────────────────────
    if data == "menu":
        await edit(
            f"<blockquote>🎮 <b>Wordly Main Menu</b></blockquote>\n\nChoose an action:",
            main_menu_keyboard()
        )
    elif data == "help":
        await edit(help_msg(), back_keyboard("menu"))

    # ── Game modes ───────────────────────────────────────────────
    elif data in ("new_game", "daily", "blitz"):
        mode_map = {"new_game": "normal", "daily": "daily", "blitz": "blitz"}
        await q.message.delete()
        fake = update
        fake._effective_message = q.message
        await _start_game(update, ctx, mode_map[data])

    # ── Economy screens ──────────────────────────────────────────
    elif data == "wallet":
        await edit(wallet_msg(user), back_keyboard("menu"))
    elif data == "shop":
        await edit(shop_msg(user["coins"]), shop_keyboard())
    elif data == "market":
        stats = await db.get_market_stats()
        await edit(market_msg(stats), back_keyboard("menu"))
    elif data == "leaderboard":
        entries = await db.get_leaderboard(10)
        rich    = await db.get_coin_rich_list(5)
        await edit(leaderboard_msg(entries, rich), back_keyboard("menu"))
    elif data == "shop_cosmetics":
        await edit(
            f"<blockquote>🎨 <b>Cosmetics Shop</b></blockquote>\n\n"
            f"{ce(E.COIN,'🪙')} Your Balance: <b>{user['coins']} $WRD</b>\n\n"
            f"Stand out on the leaderboard with exclusive looks!",
            cosmetics_keyboard()
        )

    # ── In-game power-ups ────────────────────────────────────────
    elif data.startswith("hint_"):
        sid = data[5:]
        sess = ge.get_session(uid)
        if not sess or sess.session_id != sid:
            await q.answer("❌ No active game!", show_alert=True); return
        ok, bal = await db.deduct_coins(uid, ShopPrices.HINT)
        if not ok:
            await q.answer(f"❌ Not enough $WRD! Need {ShopPrices.HINT}.", show_alert=True); return
        hint = ge.get_possible_words_hint(sess.letters, sess.used_words)
        if hint:
            await q.answer(f"💡 Try: {hint}", show_alert=True)
        else:
            await q.answer("💡 No hints available right now!", show_alert=True)

    elif data.startswith("shuffle_"):
        sid = data[8:]
        sess = ge.get_session(uid)
        if not sess or sess.session_id != sid:
            await q.answer("❌ No active game!", show_alert=True); return
        ok, bal = await db.deduct_coins(uid, ShopPrices.SHUFFLE)
        if not ok:
            await q.answer(f"❌ Not enough $WRD! Need {ShopPrices.SHUFFLE}.", show_alert=True); return
        sess.letters = ge.generate_letters(len(sess.letters))
        letter_display = "  ".join([f"<b>{l}</b>" for l in sess.letters])
        await q.answer("🔄 New letters!", show_alert=False)
        try:
            await q.edit_message_text(
                f"<blockquote>🔄 <b>Letters Shuffled!</b></blockquote>\n\n"
                f"🔤 <b>New Letters:</b>\n┌─────────────────┐\n│  {letter_display}  │\n└─────────────────┘\n\n"
                f"⏱ Time left: <b>{sess.time_left()}s</b>  |  Score: <b>{sess.score}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=game_keyboard(sid)
            )
        except Exception:
            pass

    elif data.startswith("freeze_"):
        sid = data[7:]
        sess = ge.get_session(uid)
        if not sess or sess.session_id != sid:
            await q.answer("❌ No active game!", show_alert=True); return
        ok, bal = await db.deduct_coins(uid, ShopPrices.TIME_FREEZE)
        if not ok:
            await q.answer(f"❌ Not enough $WRD! Need {ShopPrices.TIME_FREEZE}.", show_alert=True); return
        sess.add_freeze(10)
        await q.answer("⏱ +10 seconds added!", show_alert=True)

    elif data.startswith("letter_"):
        sid = data[7:]
        sess = ge.get_session(uid)
        if not sess or sess.session_id != sid:
            await q.answer("❌ No active game!", show_alert=True); return
        ok, bal = await db.deduct_coins(uid, ShopPrices.LETTER_UNLOCK)
        if not ok:
            await q.answer(f"❌ Not enough $WRD! Need {ShopPrices.LETTER_UNLOCK}.", show_alert=True); return
        import random as rnd
        new_letter = rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        sess.letters.append(new_letter)
        await q.answer(f"🔓 New letter added: {new_letter}", show_alert=True)

    elif data.startswith("endgame_"):
        sid = data[8:]
        sess = ge.get_session(uid)
        if not sess or sess.session_id != sid:
            await q.answer("No active game.", show_alert=True); return
        await _finish_game(update, ctx, uid)

    # ── Shop purchases ───────────────────────────────────────────
    elif data.startswith("buy_"):
        item = data[4:]
        price_map = {
            "hint":    ShopPrices.HINT,
            "letter":  ShopPrices.LETTER_UNLOCK,
            "shuffle": ShopPrices.SHUFFLE,
            "freeze":  ShopPrices.TIME_FREEZE,
            "shield":  ShopPrices.STREAK_SHIELD,
            "mystery": ShopPrices.MYSTERY_BOX,
            "title":   ShopPrices.CUSTOM_TITLE,
            "theme":   ShopPrices.PROFILE_THEME,
            "frame":   ShopPrices.AVATAR_FRAME,
        }
        if item not in price_map:
            return
        price = price_map[item]
        ok, new_bal = await db.deduct_coins(uid, price)
        if not ok:
            await edit(
                f"<blockquote>❌ <b>Not enough $WRD!</b></blockquote>\n\n"
                f"You need <b>{price} $WRD</b> but have <b>{user['coins']} $WRD</b>.\n\n"
                f"Play more games to earn coins!",
                back_keyboard("shop")
            )
            return
        await db.log_purchase(uid, item, price)

        if item == "mystery":
            win = random.randint(ShopPrices.MYSTERY_BOX_MIN, ShopPrices.MYSTERY_BOX_MAX)
            await db.add_coins(uid, win, "mystery_box")
            result_text = (
                f"<blockquote>📦 <b>Mystery Box Opened!</b></blockquote>\n\n"
                f"You won <b>{win} $WRD</b>! {'🎉 Lucky!' if win > 50 else '🙂 Not bad!'}\n\n"
                f"{ce(E.COIN,'🪙')} New Balance: <b>{new_bal + win} $WRD</b>"
            )
        elif item == "shield":
            await db.users_col.update_one({"user_id": uid}, {"$set": {"streak_shield": True}})
            result_text = (
                f"<blockquote>🛡 <b>Streak Shield Activated!</b></blockquote>\n\n"
                f"Your next missed day won't reset your streak.\n\n"
                f"{ce(E.COIN,'🪙')} New Balance: <b>{new_bal} $WRD</b>"
            )
        else:
            await db.grant_item(uid, item)
            result_text = (
                f"<blockquote>✅ <b>Purchase Successful!</b></blockquote>\n\n"
                f"🎒 <b>{item.replace('_',' ').title()}</b> added to your inventory!\n\n"
                f"{ce(E.COIN,'🪙')} New Balance: <b>{new_bal} $WRD</b>"
            )
        await edit(result_text, back_keyboard("shop"))


# ╔══════════════════════════════════════════════════════════════╗
# ║                OWNER COMMANDS                                ║
# ╚══════════════════════════════════════════════════════════════╝

@owner_only
async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stats = await db.get_owner_stats()
    await safe_reply(update, owner_stats_msg(stats))


@owner_only
async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await safe_reply(
            update,
            "📢 <b>Broadcast Usage:</b>\n"
            "<code>/broadcast Your message here</code>\n\n"
            "Supports HTML formatting."
        )
        return
    message = " ".join(ctx.args)
    user_ids = await db.get_all_user_ids()
    total = len(user_ids)
    sent = failed = 0
    status_msg = await safe_reply(
        update,
        f"📢 Broadcasting to <b>{total}</b> users...\nPlease wait."
    )
    for uid in user_ids:
        try:
            await ctx.bot.send_message(
                chat_id=uid,
                text=f"<blockquote>📢 <b>Announcement from Wordly Bot</b></blockquote>\n\n{message}",
                parse_mode=ParseMode.HTML
            )
            sent += 1
        except Exception:
            failed += 1
        if (sent + failed) % 50 == 0:
            await asyncio.sleep(1)   # Rate limit respect
    await db.log_broadcast(OWNER_ID, message, sent, failed)
    await safe_reply(
        update,
        f"<blockquote>✅ <b>Broadcast Complete</b></blockquote>\n\n"
        f"✅ Sent:    <b>{sent}</b>\n"
        f"❌ Failed:  <b>{failed}</b>\n"
        f"📊 Total:   <b>{total}</b>"
    )


@owner_only
async def cmd_ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await safe_reply(update, "Usage: /ban <user_id>"); return
    target = int(ctx.args[0])
    await db.ban_user(target)
    await safe_reply(update, f"⛔ User <code>{target}</code> has been banned.")


@owner_only
async def cmd_unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await safe_reply(update, "Usage: /unban <user_id>"); return
    target = int(ctx.args[0])
    await db.unban_user(target)
    await safe_reply(update, f"✅ User <code>{target}</code> has been unbanned.")


@owner_only
async def cmd_addcoins(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await safe_reply(update, "Usage: /addcoins <user_id> <amount>"); return
    target, amount = int(ctx.args[0]), int(ctx.args[1])
    new_bal = await db.add_coins(target, amount, "owner_grant")
    await safe_reply(update, f"✅ Added <b>{amount} $WRD</b> to <code>{target}</code>. New balance: <b>{new_bal}</b>")


# ╔══════════════════════════════════════════════════════════════╗
# ║                      MAIN ENTRY                              ║
# ╚══════════════════════════════════════════════════════════════╝

async def post_init(app: Application):
    await db.connect()
    # Always delete any existing webhook/polling session to prevent Conflict errors
    await app.bot.delete_webhook(drop_pending_updates=True)
    log.info("✅ Webhook cleared, bot started")


async def post_shutdown(app: Application):
    await db.disconnect()
    log.info("Bot shutdown")


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("menu",      cmd_menu))
    app.add_handler(CommandHandler("new",       cmd_new))
    app.add_handler(CommandHandler("blitz",     cmd_blitz))
    app.add_handler(CommandHandler("daily",     cmd_daily))
    app.add_handler(CommandHandler("wallet",    cmd_wallet))
    app.add_handler(CommandHandler("shop",      cmd_shop))
    app.add_handler(CommandHandler("market",    cmd_market))
    app.add_handler(CommandHandler("top",       cmd_top))
    app.add_handler(CommandHandler("profile",   cmd_profile))
    app.add_handler(CommandHandler("streak",    cmd_streak))

    # Owner commands
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("ban",       cmd_ban))
    app.add_handler(CommandHandler("unban",     cmd_unban))
    app.add_handler(CommandHandler("addcoins",  cmd_addcoins))

    # Callbacks & messages
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_word))

    if USE_WEBHOOK and WEBHOOK_URL:
        webhook_path = "/webhook"
        full_webhook_url = WEBHOOK_URL.rstrip("/") + webhook_path
        log.info(f"🌐 Starting webhook → {full_webhook_url} on port {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        log.info("🔄 Starting polling")
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )


if __name__ == "__main__":
    main()
