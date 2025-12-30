
# 🌐 Telegram Translation Bot (Fast & Lightweight)

A fast, production-ready Telegram translation bot with automatic language
detection, persistent settings, and in-memory caching.

---

## ✨ Features

- Auto language detection
- Per-chat translation toggle
- Per-user translation toggle
- Target language selection (30 languages)
- SQLite persistence
- In-memory LRU cache (very fast)
- Rate-limit protection
- Caption translation
- No external cache required

---

## 🌍 Supported Languages

English (en), Russian (ru), Hindi (hi), Bengali (bn), Spanish (es),
French (fr), German (de), Italian (it), Portuguese (pt), Turkish (tr),
Arabic (ar), Urdu (ur), Persian (fa), Japanese (ja), Korean (ko),
Chinese Simplified (zh-cn), Chinese Traditional (zh-tw), Vietnamese (vi),
Thai (th), Indonesian (id), Malay (ms), Dutch (nl), Polish (pl),
Ukrainian (uk), Romanian (ro), Greek (el), Swedish (sv),
Norwegian (no), Finnish (fi), Hebrew (he)

---

## 🤖 Commands

### Chat Controls
- `/translate_on`
- `/translate_off`
- `/setlang <code>`

### User Controls
- `/user_on`
- `/user_off`

### Info
- `/languages`
- `/help`
- `/botinfo`

---

## 🚀 Installation Guide

### 1️⃣ Clone Repository
```bash
git clone https://github.com/itzyour-roy/telegram-translation-bot.git
cd telegram-translation-bot
````

### 2️⃣ Install Dependencies

```bash
pip install python-telegram-bot==21.6 deep-translator
```

### 3️⃣ Set Bot Token

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

### 4️⃣ Run the Bot

```bash
python bot_enterprise.py
```

---

## 🧠 Performance Notes

* In-memory cache removes repeated API calls
* Async executor prevents blocking
* SQLite is used only for settings (very low overhead)

---

## 🔐 Security

* No hardcoded tokens
* Safe for public groups
* Environment-variable based configuration

---

## 👑 Credits

Created by
**[https://github.com/itzyour-roy](https://github.com/itzyour-roy)**

---

## 📜 License

MIT License

```

---


