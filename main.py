import os
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from threading import Thread
import time

from flask import Flask
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


async def update_time(bot):
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
            next_minute = (
                now + timedelta(minutes=1)
            ).replace(second=0, microsecond=0)

            sleep_time = (next_minute - now).total_seconds()

            await asyncio.sleep(sleep_time)

        except Exception as e:
            print("Telegram Error:", e, flush=True)
            await asyncio.sleep(10)


async def delete_service_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        message = update.channel_post

        if message is None:
            return

        # فقط پیام‌های سرویس/تغییرات کانال
        if message.new_chat_title:
            await message.delete()
            print("Deleted channel title service message", flush=True)

    except Exception as e:
        print("Delete Error:", e, flush=True)


async def start():
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            delete_service_message
        )
    )

    await application.initialize()
    await application.start()

    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES
    )

    print("Bot started ✅", flush=True)

    asyncio.create_task(
        update_time(application.bot)
    )

    while True:
        await asyncio.sleep(3600)


def start_bot():
    while True:
        try:
            asyncio.run(start())

        except Exception as e:
            print("Bot crashed:", e, flush=True)
            time.sleep(5)


Thread(
    target=run_web,
    daemon=True
).start()

start_bot()
