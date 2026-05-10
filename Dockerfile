# ╔══════════════════════════════════════════════════════════════╗
# ║       Wordly Bot — Heroku Docker Container                   ║
# ║       Optimized for 2x Standard Dyno                        ║
# ╚══════════════════════════════════════════════════════════════╝

FROM python:3.12-slim

# ── System deps ──────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── App directory ────────────────────────────────────────────────
WORKDIR /app

# ── Install Python deps (cached layer) ──────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Copy source ──────────────────────────────────────────────────
COPY . .

# ── Heroku sets PORT env var automatically ───────────────────────
ENV PORT=8443
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── Expose port (Heroku ignores this but good practice) ──────────
EXPOSE $PORT

# ── Run the bot ──────────────────────────────────────────────────
CMD ["python", "bot.py"]
