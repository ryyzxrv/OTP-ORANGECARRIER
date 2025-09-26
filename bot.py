import asyncio
import os
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config from ENV ---
ORANGE_BASE = "https://www.orangecarrier.com"
ORANGE_LOGIN = ORANGE_BASE + "/login"
ORANGE_CDR_PAGE = ORANGE_BASE + "/CDR/mycdrs"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

# Accounts env me JSON ke form me daalna hoga
# Example: [{"email":"user1@example.com","password":"pass1"}]
ACCOUNTS = json.loads(os.getenv("ACCOUNTS", "[]"))

seen_ids = set()


async def fetch_orange_cdr(client: httpx.AsyncClient, email: str, password: str) -> list:
    """Login to Orange Carrier and fetch CDR records for one account"""
    r = await client.get(ORANGE_LOGIN)
    soup = BeautifulSoup(r.text, "html.parser")

    token = None
    inp = soup.find("input", {"name": "_token"})
    if inp and inp.get("value"):
        token = inp["value"]

    login_data = {"email": email, "password": password}
    if token:
        login_data["_token"] = token

    await client.post(ORANGE_LOGIN, data=login_data, follow_redirects=True)

    res = await client.get(ORANGE_CDR_PAGE)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = []
    table = soup.find("table")
    if table:
        tbody = table.find("tbody")
        for tr in tbody.find_all("tr"):
            cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if len(cols) >= 5:
                cli = cols[0]
                to_num = cols[1]
                time_str = cols[2]
                duration = cols[3]
                call_type = cols[4]

                try:
                    parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
                except Exception:
                    parsed_time = time_str

                uid = f"{email}_{cli}_{parsed_time}"

                rows.append({
                    "id": uid,
                    "cli": cli,
                    "to": to_num,
                    "time": parsed_time,
                    "duration": duration,
                    "type": call_type,
                    "account": email
                })
    return rows


async def send_to_telegram(app: Application, record: dict):
    """Send one record to Telegram"""
    msg = (
        f"👤 *Account:* {record['account']}\n"
        f"📞 *CLI:* {record['cli']}\n"
        f"➡️ *To:* {record['to']}\n"
        f"⏱ *Time:* {record['time']}\n"
        f"⏳ *Duration:* {record['duration']}\n"
        f"📌 *Type:* {record['type']}"
    )
    await app.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")


async def worker(app: Application, email: str, password: str):
    """Loop ek account ke liye"""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        while True:
            try:
                records = await fetch_orange_cdr(client, email, password)
                for rec in records:
                    if rec["id"] not in seen_ids:
                        seen_ids.add(rec["id"])
                        await send_to_telegram(app, rec)
            except Exception as e:
                logger.warning(f"⚠️ {email} error: {e}")
            await asyncio.sleep(5)


# --- Heartbeat (har ghante ek baar message) ---
async def heartbeat(app: Application):
    while True:
        try:
            await app.bot.send_message(CHAT_ID, "✅ Bot active hai, sab sahi chal raha hai.")
        except Exception as e:
            logger.error("Heartbeat error: %s", e)
        await asyncio.sleep(3600)


# --- Telegram command handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is running and active!")


async def main():
    if not BOT_TOKEN or not CHAT_ID or not ACCOUNTS:
        logger.error("❌ BOT_TOKEN / CHAT_ID / ACCOUNTS env variables missing!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start_command))

    # Start workers
    for acc in ACCOUNTS:
        asyncio.create_task(worker(app, acc["email"], acc["password"]))

    # Heartbeat
    asyncio.create_task(heartbeat(app))

    # Proper lifecycle for polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
