"""
database.py — All MongoDB operations for Wordly Bot
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date
import logging

from config import MONGO_URI, DB_NAME

log = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
db = None

# ── Collections ─────────────────────────────────────────────────
users_col       = None
games_col       = None
words_col       = None
shop_col        = None
broadcast_col   = None
stats_col       = None


async def connect():
    global client, db
    global users_col, games_col, words_col, shop_col, broadcast_col, stats_col
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    users_col     = db["users"]
    games_col     = db["games"]
    words_col     = db["words_used"]
    shop_col      = db["shop_logs"]
    broadcast_col = db["broadcasts"]
    stats_col     = db["bot_stats"]

    # Indexes
    await users_col.create_index("user_id", unique=True)
    await games_col.create_index([("user_id", 1), ("date", -1)])
    await words_col.create_index([("user_id", 1), ("session_id", 1)])
    log.info("✅ MongoDB connected")


async def disconnect():
    if client:
        client.close()


# ╔══════════════════════════════════════════════════════════════╗
# ║                      USER OPERATIONS                         ║
# ╚══════════════════════════════════════════════════════════════╝

async def get_user(user_id: int) -> dict:
    return await users_col.find_one({"user_id": user_id})


async def upsert_user(user_id: int, username: str, full_name: str) -> dict:
    now = datetime.utcnow()
    # Check if user already exists to track new registrations
    existing = await users_col.find_one({"user_id": user_id})
    if existing is None:
        # New user — insert with all defaults
        doc = {
            "user_id":      user_id,
            "username":     username,
            "full_name":    full_name,
            "coins":        0,
            "total_score":  0,
            "games_played": 0,
            "words_found":  0,
            "streak":       0,
            "max_streak":   0,
            "last_played":  None,
            "streak_shield":False,
            "inventory":    {},
            "rank":         "Beginner",
            "joined_at":    now,
            "referred_by":  None,
            "referrals":    0,
            "personal_best":0,
            "title":        None,
            "theme":        "default",
            "avatar_frame": None,
            "last_daily":   None,
            "banned":       False,
            "last_seen":    now,
        }
        await users_col.insert_one(doc)
        await stats_col.update_one(
            {"_id": "global"},
            {"$inc": {"total_users": 1}, "$set": {"updated_at": now}},
            upsert=True
        )
        return doc
    else:
        # Existing user — only update mutable fields (never overlap with $setOnInsert fields)
        result = await users_col.find_one_and_update(
            {"user_id": user_id},
            {"$set": {
                "username":  username,
                "full_name": full_name,
                "last_seen": now,
            }},
            return_document=True
        )
        return result


async def add_coins(user_id: int, amount: int, reason: str = "") -> int:
    result = await users_col.find_one_and_update(
        {"user_id": user_id},
        {"$inc": {"coins": amount}},
        return_document=True
    )
    await stats_col.update_one(
        {"_id": "global"},
        {"$inc": {"total_coins_earned": amount}},
        upsert=True
    )
    return result["coins"] if result else 0


async def deduct_coins(user_id: int, amount: int) -> tuple[bool, int]:
    user = await get_user(user_id)
    if not user or user["coins"] < amount:
        return False, user["coins"] if user else 0
    result = await users_col.find_one_and_update(
        {"user_id": user_id, "coins": {"$gte": amount}},
        {"$inc": {"coins": -amount}},
        return_document=True
    )
    if result:
        await stats_col.update_one(
            {"_id": "global"},
            {"$inc": {"total_coins_spent": amount}},
            upsert=True
        )
        return True, result["coins"]
    return False, user["coins"]


async def update_streak(user_id: int) -> dict:
    user = await get_user(user_id)
    today = date.today().isoformat()
    last = user.get("last_played")
    streak = user.get("streak", 0)
    shield = user.get("streak_shield", False)

    if last == today:
        return {"streak": streak, "bonus": 0, "new_day": False}

    yesterday = (date.today().replace(day=date.today().day - 1)).isoformat()
    if last == yesterday:
        streak += 1
    elif shield and last:
        streak += 1  # Shield saved the streak
        await users_col.update_one({"user_id": user_id}, {"$set": {"streak_shield": False}})
    else:
        streak = 1

    bonus = 0
    from config import GameSettings
    if streak == 3:   bonus = GameSettings.STREAK_3_BONUS
    elif streak == 7: bonus = GameSettings.STREAK_7_BONUS
    elif streak % 7 == 0: bonus = GameSettings.STREAK_7_BONUS

    max_streak = max(streak, user.get("max_streak", 0))
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"streak": streak, "last_played": today, "max_streak": max_streak}}
    )
    return {"streak": streak, "bonus": bonus, "new_day": True}


async def update_rank(user_id: int, total_score: int):
    if total_score >= 5000:   rank = "Lexicon God"
    elif total_score >= 2000: rank = "Word Master"
    elif total_score >= 1000: rank = "Wordsmith"
    elif total_score >= 500:  rank = "Linguist"
    elif total_score >= 200:  rank = "Explorer"
    elif total_score >= 50:   rank = "Learner"
    else:                     rank = "Beginner"
    await users_col.update_one({"user_id": user_id}, {"$set": {"rank": rank}})
    return rank


async def save_game(user_id: int, session_id: str, score: int, words: list,
                    mode: str, coins_earned: int, duration: int):
    now = datetime.utcnow()
    await games_col.insert_one({
        "user_id":      user_id,
        "session_id":   session_id,
        "score":        score,
        "words":        words,
        "mode":         mode,
        "coins_earned": coins_earned,
        "duration":     duration,
        "date":         now.date().isoformat(),
        "played_at":    now,
    })
    user = await users_col.find_one_and_update(
        {"user_id": user_id},
        {
            "$inc": {
                "total_score":  score,
                "games_played": 1,
                "words_found":  len(words),
            }
        },
        return_document=True
    )
    pb_bonus = 0
    if score > user.get("personal_best", 0):
        from config import GameSettings
        pb_bonus = GameSettings.PB_BONUS
        await users_col.update_one({"user_id": user_id}, {"$set": {"personal_best": score}})
    await update_rank(user_id, user["total_score"] + score)
    await stats_col.update_one(
        {"_id": "global"},
        {"$inc": {"total_games": 1, "total_words_found": len(words)}},
        upsert=True
    )
    return pb_bonus


# ╔══════════════════════════════════════════════════════════════╗
# ║                    LEADERBOARD                               ║
# ╚══════════════════════════════════════════════════════════════╝

async def get_leaderboard(limit: int = 10) -> list:
    cursor = users_col.find(
        {"banned": False},
        {"user_id": 1, "full_name": 1, "username": 1, "total_score": 1,
         "rank": 1, "coins": 1, "streak": 1}
    ).sort("total_score", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_coin_rich_list(limit: int = 5) -> list:
    cursor = users_col.find(
        {"banned": False},
        {"user_id": 1, "full_name": 1, "coins": 1, "rank": 1}
    ).sort("coins", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ╔══════════════════════════════════════════════════════════════╗
# ║                    SHOP OPERATIONS                           ║
# ╚══════════════════════════════════════════════════════════════╝

async def log_purchase(user_id: int, item: str, price: int):
    await shop_col.insert_one({
        "user_id":    user_id,
        "item":       item,
        "price":      price,
        "bought_at":  datetime.utcnow(),
    })


async def grant_item(user_id: int, item: str, value=True):
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {f"inventory.{item}": value}}
    )


async def get_inventory(user_id: int) -> dict:
    user = await get_user(user_id)
    return user.get("inventory", {}) if user else {}


# ╔══════════════════════════════════════════════════════════════╗
# ║                    MARKET STATS                              ║
# ╚══════════════════════════════════════════════════════════════╝

async def get_market_stats() -> dict:
    stats = await stats_col.find_one({"_id": "global"}) or {}
    today = date.today().isoformat()
    today_games = await games_col.count_documents({"date": today})
    today_users = await users_col.count_documents({"last_played": today})
    total_supply = await users_col.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$coins"}}}
    ]).to_list(1)
    supply = total_supply[0]["total"] if total_supply else 0
    return {
        "total_users":       stats.get("total_users", 0),
        "total_games":       stats.get("total_games", 0),
        "total_coins_earned":stats.get("total_coins_earned", 0),
        "total_coins_spent": stats.get("total_coins_spent", 0),
        "circulating_supply":supply,
        "today_games":       today_games,
        "today_active":      today_users,
    }


# ╔══════════════════════════════════════════════════════════════╗
# ║                OWNER STATS (Dashboard)                       ║
# ╚══════════════════════════════════════════════════════════════╝

async def get_owner_stats() -> dict:
    market = await get_market_stats()
    total_users  = await users_col.count_documents({})
    banned_users = await users_col.count_documents({"banned": True})
    today = date.today().isoformat()
    new_today    = await users_col.count_documents({"joined_at": {"$gte": datetime.utcnow().replace(hour=0,minute=0,second=0)}})
    return {
        **market,
        "total_registered": total_users,
        "banned_users":     banned_users,
        "new_today":        new_today,
        "total_words_found":market.get("total_games", 0),
    }


# ╔══════════════════════════════════════════════════════════════╗
# ║                    BROADCAST                                 ║
# ╚══════════════════════════════════════════════════════════════╝

async def get_all_user_ids() -> list:
    cursor = users_col.find({"banned": False}, {"user_id": 1})
    docs = await cursor.to_list(length=None)
    return [d["user_id"] for d in docs]


async def log_broadcast(owner_id: int, message: str, sent: int, failed: int):
    await broadcast_col.insert_one({
        "owner_id":    owner_id,
        "message":     message,
        "sent":        sent,
        "failed":      failed,
        "broadcasted_at": datetime.utcnow(),
    })


# ─── Daily challenge tracking ────────────────────────────────────
async def claim_daily(user_id: int) -> bool:
    today = date.today().isoformat()
    user = await get_user(user_id)
    if user and user.get("last_daily") == today:
        return False
    await users_col.update_one({"user_id": user_id}, {"$set": {"last_daily": today}})
    return True


# ─── Ban / Unban ────────────────────────────────────────────────
async def ban_user(user_id: int):
    await users_col.update_one({"user_id": user_id}, {"$set": {"banned": True}})

async def unban_user(user_id: int):
    await users_col.update_one({"user_id": user_id}, {"$set": {"banned": False}})
