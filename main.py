import os
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from threading import Thread
import time

from flask import Flask
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


async def update_time():
    while True:
        try:
            now = datetime.now(ZoneInfo("Asia/Tehran"))
            time_text = now.strftime("%H:%M")

            await bot.set_chat_title(
                chat_id=CHANNEL_ID,
                title=time_text
            )

            print("Updated:", time_text, flush=True)

            now = datetime.now(ZoneInfo("Asia/Tehran"))
            next_minute = (now + timedelta(minutes=1)).replace(
                second=0,
                microsecond=0
            )

            sleep_time = (next_minute - now).total_seconds()
            await asyncio.sleep(sleep_time)

        except Exception as e:
            print("Telegram Error:", e, flush=True)
            await asyncio.sleep(10)


def start_bot():
    while True:
        try:
            asyncio.run(update_time())
        except Exception as e:
            print("Bot crashed:", e, flush=True)
            time.sleep(5)


Thread(target=run_web, daemon=True).start()

start_bot()
