"""
game_engine.py — Core game logic for Wordly Bot
"""

import random
import string
import asyncio
import uuid
import aiohttp
import logging
from datetime import datetime

from config import GameSettings, DICT_API_URL

log = logging.getLogger(__name__)

# ── Letter frequency pool (Scrabble-inspired, English-biased) ────
LETTER_POOL = (
    "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMM"
    "NNNNNNOOOOOOOOPPQRRRRRRSSSSSSTTTTTTTUUUUUVVWWXYYZ"
)

# ── Word validation cache (in-memory LRU style) ──────────────────
_word_cache: dict[str, bool] = {}
MAX_CACHE = 5000


async def validate_word_api(word: str) -> bool:
    word = word.upper()
    if word in _word_cache:
        return _word_cache[word]
    try:
        url = DICT_API_URL.format(word=word.lower())
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as sess:
            async with sess.get(url) as r:
                valid = r.status == 200
    except Exception:
        # Fallback: assume valid if API unreachable (prevents game breaking)
        valid = True
    if len(_word_cache) >= MAX_CACHE:
        _word_cache.clear()
    _word_cache[word] = valid
    return valid


def generate_letters(count: int = None) -> list[str]:
    """Generate a balanced, game-friendly set of letters."""
    count = count or GameSettings.LETTERS_COUNT
    # Guarantee at least 2 vowels
    vowels    = random.sample("AEIOU", 2)
    consonants= random.sample("BCDFGHJKLMNPRSTW", count - 2)
    letters   = vowels + consonants
    random.shuffle(letters)
    return letters


def get_possible_words_hint(letters: list[str], used_words: set) -> str | None:
    """Return one valid short word from letters as a hint (local fast check)."""
    common = [
        "CAT","DOG","RAT","BAT","HAT","MAT","SAT","PAT",
        "RAN","CAN","MAN","FAN","PAN","TAN","VAN","BAN",
        "SIT","HIT","BIT","FIT","KIT","WIT","PIT","LIT",
        "TOP","HOP","MOP","POP","COP","DOP","ROT","DOT",
        "BOT","HOT","POT","LOT","NOT","GOT","JOT",
        "RUN","GUN","BUN","SUN","NUN","FUN","PUN",
        "ATE","LATE","GATE","MATE","FATE","DATE","RATE",
        "RING","SING","KING","WING","PING","DING",
        "STAR","SCAR","CHAR","SPAR","FARM","HARM","LARD",
    ]
    letter_set = [l.upper() for l in letters]
    random.shuffle(common)
    for w in common:
        if w in used_words:
            continue
        tmp = letter_set.copy()
        ok = True
        for ch in w:
            if ch in tmp:
                tmp.remove(ch)
            else:
                ok = False; break
        if ok:
            return w
    return None


def calc_score(word: str) -> int:
    l = len(word)
    pts = GameSettings.WORD_POINTS
    if l <= 3:  return pts[3]
    if l == 4:  return pts[4]
    if l == 5:  return pts[5]
    if l == 6:  return pts[6]
    if l == 7:  return pts[7]
    return pts[8]   # 8–12 all get max


def calc_coins(word: str) -> int:
    return calc_score(word)   # 1:1 parity by default


# ╔══════════════════════════════════════════════════════════════╗
# ║                    GAME SESSION                              ║
# ╚══════════════════════════════════════════════════════════════╝

class GameSession:
    def __init__(self, user_id: int, mode: str = "normal", extra_letter: str = None):
        self.session_id   = str(uuid.uuid4())[:8]
        self.user_id      = user_id
        self.mode         = mode          # "normal" | "blitz" | "daily"
        self.letters      = generate_letters(GameSettings.LETTERS_COUNT)
        if extra_letter:
            self.letters.append(extra_letter.upper())
            random.shuffle(self.letters)
        self.used_words:  set  = set()
        self.score:       int  = 0
        self.coins_earned:int  = 0
        self.start_time        = datetime.utcnow()
        self.active:      bool = True
        self.frozen_secs: int  = 0          # Time Freeze powerup
        duration = GameSettings.BLITZ_DURATION if mode == "blitz" else GameSettings.ROUND_DURATION
        self.end_time          = self.start_time.timestamp() + duration

    def time_left(self) -> int:
        left = int(self.end_time - datetime.utcnow().timestamp()) + self.frozen_secs
        return max(0, left)

    def is_expired(self) -> bool:
        return self.time_left() <= 0

    def add_freeze(self, secs: int = 10):
        self.frozen_secs += secs

    def word_valid_locally(self, word: str) -> tuple[bool, str]:
        """Fast local checks before hitting the API."""
        w = word.upper().strip()
        if len(w) < GameSettings.MIN_WORD_LEN:
            return False, f"Too short! Minimum {GameSettings.MIN_WORD_LEN} letters."
        if len(w) > GameSettings.MAX_WORD_LEN:
            return False, f"Too long! Maximum {GameSettings.MAX_WORD_LEN} letters."
        if w in self.used_words:
            return False, "Already used that word this round!"
        # Letters check (repetition allowed — each letter can be reused freely)
        return True, ""

    async def submit_word(self, word: str) -> dict:
        word = word.upper().strip()
        if self.is_expired():
            self.active = False
            return {"ok": False, "reason": "⏱ Time's up! Game over."}
        ok, reason = self.word_valid_locally(word)
        if not ok:
            return {"ok": False, "reason": reason}
        valid = await validate_word_api(word)
        if not valid:
            return {"ok": False, "reason": f"❌ «{word}» is not a valid English word."}
        pts   = calc_score(word)
        coins = calc_coins(word)
        self.score        += pts
        self.coins_earned += coins
        self.used_words.add(word)
        return {
            "ok":     True,
            "word":   word,
            "points": pts,
            "coins":  coins,
            "total_score":  self.score,
            "total_coins":  self.coins_earned,
            "words_found":  len(self.used_words),
        }

    def summary(self) -> dict:
        return {
            "session_id":   self.session_id,
            "mode":         self.mode,
            "score":        self.score,
            "coins_earned": self.coins_earned,
            "words":        list(self.used_words),
            "word_count":   len(self.used_words),
            "duration":     int((datetime.utcnow() - self.start_time).total_seconds()),
        }


# ── In-memory session store ──────────────────────────────────────
_sessions: dict[int, GameSession] = {}


def create_session(user_id: int, mode: str = "normal", extra_letter: str = None) -> GameSession:
    sess = GameSession(user_id, mode, extra_letter)
    _sessions[user_id] = sess
    return sess


def get_session(user_id: int) -> GameSession | None:
    return _sessions.get(user_id)


def end_session(user_id: int) -> GameSession | None:
    return _sessions.pop(user_id, None)


def has_active_session(user_id: int) -> bool:
    sess = _sessions.get(user_id)
    if not sess:
        return False
    if sess.is_expired():
        _sessions.pop(user_id, None)
        return False
    return True
