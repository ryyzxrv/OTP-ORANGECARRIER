

🔧 Short GitHub Repo Description

A multi-account Orange Carrier CDR fetcher with Telegram bot integration. 
Fetches CDR records from multiple Orange Carrier accounts, sends them to a Telegram group, 
supports /start command, and hourly heartbeat messages. Ready for Heroku deployment.


---

📄 Suggested README.md Content

# Orange Carrier Telegram Bot

🚀 A Python bot that logs into **multiple Orange Carrier accounts**, fetches **CDR records**, and sends them directly to a Telegram group/channel.

### ✨ Features
- ✅ Multi-account support (parallel login & CDR fetch)
- ✅ Sends new call records (CLI, To, Time, Duration, Type) to Telegram
- ✅ Prevents duplicate messages
- ✅ `/start` command support
- ✅ Hourly heartbeat message (`Bot active hai...`)
- ✅ Heroku-ready (Procfile, runtime.txt, app.json included)

---

### 🛠 Deployment

#### 1. Clone Repo
```bash
git clone https://github.com/yourname/orange-carrier-bot.git
cd orange-carrier-bot

2. Set Environment Variables

On Heroku (or locally with .env):

BOT_TOKEN → Your Telegram Bot Token

CHAT_ID → Telegram Group/Chat ID (e.g., -100123456789)

ACCOUNTS → JSON list of Orange Carrier accounts

[
  {"email": "user1@example.com", "password": "pass1"},
  {"email": "user2@example.com", "password": "pass2"}
]


3. Deploy to Heroku

Click below 👇
<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/Akash8t2/ORANGECARRIER"> <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-black?style=for-the-badge&logo=heroku" width="250" height="50"/></a></p>




---

📂 Project Structure

orange-carrier-bot/
│── orange_bot.py       # Main bot script
│── requirements.txt    # Python dependencies
│── Procfile            # Heroku process definition
│── runtime.txt         # Python runtime version
│── app.json            # Heroku deploy config


---

⚡ Tech Stack

Python 3.10+

httpx (HTTP client)

BeautifulSoup4 (HTML parsing)

python-telegram-bot (Telegram API)



---

📜 License

MIT License © 2025

---
