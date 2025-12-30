#!/usr/bin/env python3
"""
Enterprise Telegram Translation Bot
-----------------------------------
Features:
• Auto language detection
• 30 supported target languages
• Per-chat enable/disable (SQLite)
• Per-user enable/disable (SQLite)
• Target language selection per chat
• In-memory LRU cache (fast)
• Rate limiting
• Caption translation supported

Credits:
https://github.com/itzyour-roy
"""

import os
import re
import time
import asyncio
import logging
import sqlite3
from typing import Optional
from functools import lru_cache

from deep_translator import GoogleTranslator
from telegram import Update, Message
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translator")

# =========================
# SUPPORTED LANGUAGES (30)
# =========================
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ru": "Russian",
    "hi": "Hindi",
    "bn": "Bengali",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "tr": "Turkish",
    "ar": "Arabic",
    "ur": "Urdu",
    "fa": "Persian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "nl": "Dutch",
    "pl": "Polish",
    "uk": "Ukrainian",
    "ro": "Romanian",
    "el": "Greek",
    "sv": "Swedish",
    "no": "Norwegian",
    "fi": "Finnish",
    "he": "Hebrew",
}

# =========================
# DATABASE (SQLite)
# =========================
DB = sqlite3.connect("settings.db", check_same_thread=False)
CUR = DB.cursor()

CUR.execute("""
CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 1,
    target_lang TEXT DEFAULT 'en'
)
""")

CUR.execute("""
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 1
)
""")

DB.commit()

# =========================
# RATE LIMITING
# =========================
RATE_LIMIT = {}
RATE_SECONDS = 2

def is_rate_limited(key: str) -> bool:
    now = time.time()
    last = RATE_LIMIT.get(key, 0)
    if now - last < RATE_SECONDS:
        return True
    RATE_LIMIT[key] = now
    return False

# =========================
# TRANSLATION (FAST)
# =========================
def has_text(text: str) -> bool:
    return bool(re.search(r"\w", text))

def detect_lang(text: str) -> str:
    try:
        return GoogleTranslator().detect(text)
    except Exception:
        return "auto"

@lru_cache(maxsize=5000)
def cached_translate(text: str, src: str, dst: str) -> str:
    return GoogleTranslator(source=src, target=dst).translate(text)

async def translate_async(text: str, src: str, dst: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, cached_translate, text, src, dst)

# =========================
# SETTINGS ACCESS
# =========================
def chat_enabled(chat_id):
    CUR.execute("SELECT enabled FROM chat_settings WHERE chat_id=?", (chat_id,))
    row = CUR.fetchone()
    return row[0] == 1 if row else True

def user_enabled(user_id):
    CUR.execute("SELECT enabled FROM user_settings WHERE user_id=?", (user_id,))
    row = CUR.fetchone()
    return row[0] == 1 if row else True

def chat_target(chat_id):
    CUR.execute("SELECT target_lang FROM chat_settings WHERE chat_id=?", (chat_id,))
    row = CUR.fetchone()
    return row[0] if row else "en"

# =========================
# COMMANDS
# =========================
async def translate_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    CUR.execute("REPLACE INTO chat_settings(chat_id, enabled) VALUES (?,1)", (chat_id,))
    DB.commit()
    await update.message.reply_text("✅ Translation enabled in this chat")

async def translate_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    CUR.execute("REPLACE INTO chat_settings(chat_id, enabled) VALUES (?,0)", (chat_id,))
    DB.commit()
    await update.message.reply_text("⛔ Translation disabled in this chat")

async def user_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    CUR.execute("REPLACE INTO user_settings(user_id, enabled) VALUES (?,1)", (user_id,))
    DB.commit()
    await update.message.reply_text("✅ Translation enabled for you")

async def user_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    CUR.execute("REPLACE INTO user_settings(user_id, enabled) VALUES (?,0)", (user_id,))
    DB.commit()
    await update.message.reply_text("⛔ Translation disabled for you")

async def setlang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setlang <language_code>")
        return

    lang = context.args[0].lower()
    if lang not in SUPPORTED_LANGUAGES:
        await update.message.reply_text("❌ Unsupported language. Use /languages")
        return

    chat_id = update.effective_chat.id
    CUR.execute(
        "REPLACE INTO chat_settings(chat_id, target_lang) VALUES (?,?)",
        (chat_id, lang)
    )
    DB.commit()

    await update.message.reply_text(
        f"🌐 Target language set to {SUPPORTED_LANGUAGES[lang]} ({lang})"
    )

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    langs = ", ".join(f"{name} ({code})" for code, name in SUPPORTED_LANGUAGES.items())
    await update.message.reply_text(f"🌍 Supported Languages:\n{langs}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "📘 <b>Translation Bot Help</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Chat</b>\n"
        "• /translate_on\n"
        "• /translate_off\n"
        "• /setlang &lt;code&gt;\n\n"
        "<b>User</b>\n"
        "• /user_on\n"
        "• /user_off\n\n"
        "<b>Info</b>\n"
        "• /languages\n"
        "• /botinfo\n"
        "• /help\n\n"
        "Credits:\n<b>github.com/itzyour-roy</b>"
    )

async def botinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "🤖 <b>DEMIGODS Translator Bot</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "• Auto language detection\n"
        "• SQLite persistence\n"
        "• In-memory caching\n"
        "• Rate limiting\n\n"
        "Credits:\n<b>github.com/itzyour-roy</b>"
    )

# =========================
# TRANSLATION HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Optional[Message] = update.effective_message
    if not message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not chat_enabled(chat_id) or not user_enabled(user_id):
        return

    if is_rate_limited(f"{chat_id}:{user_id}"):
        return

    text = message.text or message.caption
    if not text or not has_text(text):
        return

    src = detect_lang(text)
    dst = chat_target(chat_id)
    if src == dst:
        return

    translated = await translate_async(text, src, dst)
    await message.reply_text(f"🌐 {src.upper()} → {dst.upper()}\n{translated}")

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("botinfo", botinfo))
    app.add_handler(CommandHandler("languages", languages_command))
    app.add_handler(CommandHandler("translate_on", translate_on))
    app.add_handler(CommandHandler("translate_off", translate_off))
    app.add_handler(CommandHandler("user_on", user_on))
    app.add_handler(CommandHandler("user_off", user_off))
    app.add_handler(CommandHandler("setlang", setlang))

    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    logger.info("Translation bot started (fast mode, no Redis)")
    app.run_polling()

if __name__ == "__main__":
    main()
