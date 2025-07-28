import asyncio
import os
from telethon import TelegramClient, events
import telegram
from datetime import datetime
import re
import logging

from quotes import get_quote

API_ID = int(os.getenv("API_ID"))
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "me"))
NOTIFY_CHANEL = int(os.getenv("NOTIFY_CHANEL", "me"))  # Default to 'me' if not set
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_HASH = os.getenv("API_HASH")

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console (container logs)
        logging.FileHandler("bot.log"),  # Log to file inside the container
    ],
)
logging.info("Starting Telegram client...")


# Load environment variables from .env file for local development
# from dotenv import load_dotenv
# load_dotenv()

client = TelegramClient("session", API_ID, API_HASH)


async def notify_users():
    await send_telegram_message(NOTIFY_CHANEL, get_quote())


async def send_telegram_message(chat_id: str, text: str):
    """Sends a message to the specified chat ID using the bot."""
    bot = telegram.Bot(BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logging.info(f"Message sent to chat ID {chat_id}: {text}")
    except telegram.error.TelegramError as e:
        logging.error(f"Error sending message: {e}")


@client.on(events.NewMessage)
async def handler(event):
    # if event.message:
    if event.is_group and event.message:
        today_str = datetime.now().strftime("%Y/%-m/%-d")
        pattern = rf"{today_str}/\d+\nTrading deadline:\nLondon:.*"
        if re.match(pattern, event.message.message, re.DOTALL):
            sender = await event.get_sender()
            await notify_users()


async def main():
    await client.start(phone=PHONE_NUMBER)
    await client.send_message(
        ADMIN_USER_ID, "Bot Started."
    )  # This will send the message when the bot starts
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
