import asyncio
import os
from telethon import TelegramClient, events
from datetime import datetime
import re
import logging
import telegram 

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console (container logs)
        logging.FileHandler("bot.log")  # Log to file inside the container
    ]
)
# Load environment variables from .env file for local development
# from dotenv import load_dotenv
# load_dotenv()

API_ID = int(os.getenv("API_ID"))
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "me"))
NOTIFY_CHANEL = int(os.getenv("NOTIFY_CHANEL", "me"))  # Default to 'me' if not set
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_HASH = os.getenv("API_HASH")
client = TelegramClient('session', API_ID, API_HASH)
logging.info("Starting Telegram client...")

NOTIFY_USER_IDS = [int(uid.strip()) for uid in os.getenv("NOTIFY_USER_IDS", "").split(",") if uid.strip()]
async def notify_users(msg):
    for user_id in NOTIFY_USER_IDS:
        await send_telegram_message(user_id, msg)
    await send_telegram_message(NOTIFY_CHANEL, msg)

async def send_telegram_message(chat_id:str, text:str):
    """Sends a message to the specified chat ID using the bot."""
    bot = telegram.Bot(BOT_TOKEN)
    try:
        await bot.send_message(chat_id=NOTIFY_CHANEL, text=text)
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
            msg = (
                f"Trading deadline found in thread "
                f"from {getattr(sender, 'username', 'Unknown')}: {event.message.message}"
            )
            logging.info(msg)
            await notify_users(msg)

async def main():
    await client.start(phone=PHONE_NUMBER)
    await send_telegram_message(ADMIN_USER_ID, "Bot started!")  # This will send the message when the bot starts
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())