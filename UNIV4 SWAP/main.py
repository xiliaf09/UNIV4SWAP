import os
from dotenv import load_dotenv
from telegram.ext import Application
from bot.handlers import register_handlers

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN manquant dans les variables d'environnement.")

app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

register_handlers(app)

if __name__ == "__main__":
    print("Bot Telegram Uniswap V4 en cours de démarrage...")
    app.run_polling() 