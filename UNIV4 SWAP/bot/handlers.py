from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.uniswap_v4 import buy_token_v4
import logging

async def buyv4_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 3:
            await update.message.reply_text("Usage : /buyv4 <token_address> <amount_eth> <max_fee_per_gas>")
            return
        token_address, amount_eth, max_fee_per_gas = context.args
        tx_hash, basescan_url, msg = await buy_token_v4(token_address, amount_eth, max_fee_per_gas)
        await update.message.reply_text(f"Swap envoyé !\nHash: {tx_hash}\nLien: {basescan_url}\n{msg}")
    except Exception as e:
        logging.exception("Erreur lors du swap :")
        await update.message.reply_text(f"Erreur lors du swap : {e}")

def register_handlers(app):
    app.add_handler(CommandHandler("buyv4", buyv4_command)) 