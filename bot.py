import logging
import asyncio
from datetime import datetime, timezone
import json
import os
from typing import Dict, Set
from decimal import Decimal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import httpx
from web3 import Web3
from web3.middleware import geth_poa_middleware

from config import *

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sniper.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialisation Web3
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# ABI minimal pour le router Uniswap V2
ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Adresse du router Uniswap V2 sur Base
ROUTER_ADDRESS = Web3.to_checksum_address("0x327df1e6de05895d2ab08513aadd9313fe505d86")
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

# États pour les conversations
ADD_FID, ADD_TICKER, ADD_ADDRESS, SET_AMOUNT = range(4)

class ClankerSniper:
    def __init__(self):
        self.seen_tokens: Set[str] = set()
        self.active_snipes: Dict[str, Dict] = {}
        self.snipe_amount = DEFAULT_SNIPE_AMOUNT
        self.load_seen_tokens()
        
        # Initialiser le router
        self.router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

    def load_seen_tokens(self):
        """Charge les tokens déjà vus depuis le fichier."""
        try:
            if os.path.exists('seen_tokens.json'):
                with open('seen_tokens.json', 'r') as f:
                    self.seen_tokens = set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading seen tokens: {e}")

    def save_seen_tokens(self):
        """Sauvegarde les tokens vus dans le fichier."""
        try:
            with open('seen_tokens.json', 'w') as f:
                json.dump(list(self.seen_tokens), f)
        except Exception as e:
            logger.error(f"Error saving seen tokens: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Status", callback_data='status'),
                InlineKeyboardButton("⚙️ Settings", callback_data='settings')
            ],
            [
                InlineKeyboardButton("🎯 Add FID", callback_data='add_fid'),
                InlineKeyboardButton("📝 Add Ticker", callback_data='add_ticker')
            ],
            [
                InlineKeyboardButton("🔍 Add Address", callback_data='add_address'),
                InlineKeyboardButton("❌ Remove Filter", callback_data='remove_filter')
            ],
            [
                InlineKeyboardButton("💰 Set Snipe Amount", callback_data='set_amount')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🤖 Bienvenue sur le Clanker Sniper Bot!\n\n"
            "Utilisez les boutons ci-dessous pour configurer le bot.",
            reply_markup=reply_markup
        )

    async def set_snipe_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Configure le montant de sniping en ETH"""
        if not context.args:
            await update.message.reply_text(
                "❌ Veuillez spécifier un montant en ETH.\n"
                "Exemple: /set_amount 0.1"
            )
            return
            
        try:
            amount = float(context.args[0])
            if amount <= 0:
                await update.message.reply_text("❌ Le montant doit être supérieur à 0.")
                return
                
            self.snipe_amount = amount
            await update.message.reply_text(f"✅ Montant de sniping configuré à {amount} ETH")
        except ValueError:
            await update.message.reply_text("❌ Montant invalide. Veuillez entrer un nombre.")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Affiche le statut actuel du bot"""
        status_text = "📊 Status du Sniper:\n\n"
        
        # Status des filtres
        status_text += "🎯 Filtres actifs:\n"
        status_text += f"• FIDs surveillés: {len(WATCHED_FIDS)}\n"
        status_text += f"• Tickers surveillés: {len(WATCHED_TICKERS)}\n"
        status_text += f"• Adresses surveillées: {len(WATCHED_ADDRESSES)}\n\n"
        
        # Status du wallet
        if WALLET_ADDRESS:
            balance = w3.eth.get_balance(WALLET_ADDRESS)
            balance_eth = w3.from_wei(balance, 'ether')
            status_text += f"💰 Balance: {balance_eth:.4f} ETH\n"
            status_text += f"💵 Montant de sniping: {self.snipe_amount} ETH\n"
        else:
            status_text += "❌ Aucun wallet configuré\n"
        
        # Status des snipes actifs
        if self.active_snipes:
            status_text += "\n🎯 Snipes en cours:\n"
            for token, info in self.active_snipes.items():
                status_text += f"• {info.get('name', 'Unknown')}: {info.get('status', 'Unknown')}\n"
        
        await update.message.reply_text(status_text)

    async def add_fid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ajoute un FID à surveiller"""
        if not context.args:
            await update.message.reply_text(
                "❌ Veuillez spécifier un FID.\n"
                "Exemple: /add_fid 12345"
            )
            return
            
        fid = context.args[0]
        if not fid.isdigit():
            await update.message.reply_text("❌ Le FID doit être un nombre.")
            return
            
        WATCHED_FIDS.add(fid)
        await update.message.reply_text(f"✅ FID {fid} ajouté à la liste de surveillance.")

    async def add_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ajoute un ticker à surveiller"""
        if not context.args:
            await update.message.reply_text(
                "❌ Veuillez spécifier un ticker.\n"
                "Exemple: /add_ticker PEPE"
            )
            return
            
        ticker = context.args[0].upper()
        WATCHED_TICKERS.add(ticker)
        await update.message.reply_text(f"✅ Ticker {ticker} ajouté à la liste de surveillance.")

    async def add_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ajoute une adresse Base à surveiller"""
        if not context.args:
            await update.message.reply_text(
                "❌ Veuillez spécifier une adresse.\n"
                "Exemple: /add_address 0x123..."
            )
            return
            
        address = context.args[0]
        if not w3.is_address(address):
            await update.message.reply_text("❌ Adresse invalide.")
            return
            
        WATCHED_ADDRESSES.add(address.lower())
        await update.message.reply_text(f"✅ Adresse {address} ajoutée à la liste de surveillance.")

    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retire un filtre"""
        if not context.args:
            await update.message.reply_text(
                "❌ Veuillez spécifier le type de filtre à retirer.\n"
                "Exemple: /remove_filter fid 12345"
            )
            return
            
        filter_type = context.args[0].lower()
        if len(context.args) < 2:
            await update.message.reply_text("❌ Veuillez spécifier la valeur à retirer.")
            return
            
        value = context.args[1]
        
        if filter_type == 'fid':
            if value in WATCHED_FIDS:
                WATCHED_FIDS.remove(value)
                await update.message.reply_text(f"✅ FID {value} retiré de la liste de surveillance.")
            else:
                await update.message.reply_text("❌ FID non trouvé dans la liste.")
        elif filter_type == 'ticker':
            if value.upper() in WATCHED_TICKERS:
                WATCHED_TICKERS.remove(value.upper())
                await update.message.reply_text(f"✅ Ticker {value} retiré de la liste de surveillance.")
            else:
                await update.message.reply_text("❌ Ticker non trouvé dans la liste.")
        elif filter_type == 'address':
            if value.lower() in WATCHED_ADDRESSES:
                WATCHED_ADDRESSES.remove(value.lower())
                await update.message.reply_text(f"✅ Adresse {value} retirée de la liste de surveillance.")
            else:
                await update.message.reply_text("❌ Adresse non trouvée dans la liste.")
        else:
            await update.message.reply_text("❌ Type de filtre invalide. Utilisez 'fid', 'ticker' ou 'address'.")

    async def execute_snipe(self, token_address: str, token_data: Dict):
        """Exécute le sniping d'un token"""
        try:
            # Vérifier la balance
            balance = w3.eth.get_balance(WALLET_ADDRESS)
            balance_eth = w3.from_wei(balance, 'ether')
            
            if balance_eth < self.snipe_amount:
                logger.error(f"Insufficient balance for snipe: {balance_eth} ETH")
                return False
                
            # Préparer la transaction
            amount_in = w3.to_wei(self.snipe_amount, 'ether')
            path = [WETH_ADDRESS, token_address]
            deadline = w3.eth.get_block('latest').timestamp + 300  # 5 minutes
            
            # Construire la transaction
            tx = self.router.functions.swapExactETHForTokens(
                0,  # amountOutMin (0 car slippage max)
                path,
                WALLET_ADDRESS,
                deadline
            ).build_transaction({
                'from': WALLET_ADDRESS,
                'value': amount_in,
                'gas': DEFAULT_GAS_LIMIT,
                'gasPrice': int(w3.eth.gas_price * DEFAULT_GAS_PRICE),
                'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
            })
            
            # Signer et envoyer la transaction
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Attendre la confirmation
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Snipe successful for token {token_address}")
                return True
            else:
                logger.error(f"Snipe failed for token {token_address}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing snipe: {e}")
            return False

    async def monitor_clanker(self):
        """Surveille les nouveaux tokens Clanker"""
        while True:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{CLANKER_API_URL}/tokens", params={"page": 1, "sort": "desc"})
                    response.raise_for_status()
                    data = response.json()

                    if not isinstance(data, dict) or "data" not in data:
                        logger.error("Invalid response format from Clanker API")
                        continue

                    tokens = data["data"]
                    for token in tokens:
                        contract_address = token.get('contract_address')
                        if not contract_address or contract_address in self.seen_tokens:
                            continue

                        # Vérifier les filtres
                        fid = str(token.get('requestor_fid', ''))
                        symbol = token.get('symbol', '').upper()
                        
                        if (WATCHED_FIDS and fid not in WATCHED_FIDS) or \
                           (WATCHED_TICKERS and symbol not in WATCHED_TICKERS):
                            continue

                        # Ajouter aux tokens vus
                        self.seen_tokens.add(contract_address)
                        self.save_seen_tokens()

                        # Notifier le nouveau token
                        if NOTIFY_ON_NEW_TOKEN:
                            message = (
                                f"🆕 Nouveau token détecté!\n\n"
                                f"Nom: {token.get('name', 'Unknown')}\n"
                                f"Symbole: {token.get('symbol', 'Unknown')}\n"
                                f"FID: {fid}\n"
                                f"Contract: `{contract_address}`\n"
                            )
                            # TODO: Envoyer la notification à tous les chats autorisés

                        # Exécuter le sniping
                        success = await self.execute_snipe(contract_address, token)
                        
                        if success and NOTIFY_ON_SNIPE:
                            message = (
                                f"✅ Snipe réussi!\n\n"
                                f"Token: {token.get('name', 'Unknown')} ({token.get('symbol', 'Unknown')})\n"
                                f"Montant: {self.snipe_amount} ETH\n"
                                f"Contract: `{contract_address}`\n"
                            )
                            # TODO: Envoyer la notification de succès

            except Exception as e:
                logger.error(f"Error monitoring Clanker: {e}")
                if NOTIFY_ON_ERROR:
                    # TODO: Envoyer la notification d'erreur
                    pass

            await asyncio.sleep(2)  # Attendre 2 secondes entre chaque vérification

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data
        if data == 'status':
            await self.status(update, context)
        elif data == 'settings':
            await query.answer("Fonctionnalité à venir !", show_alert=True)
        elif data == 'add_fid':
            await query.answer()
            await query.message.reply_text("Merci d'entrer le FID à ajouter :")
            return ADD_FID
        elif data == 'add_ticker':
            await query.answer()
            await query.message.reply_text("Merci d'entrer le ticker à ajouter :")
            return ADD_TICKER
        elif data == 'add_address':
            await query.answer()
            await query.message.reply_text("Merci d'entrer l'adresse à ajouter :")
            return ADD_ADDRESS
        elif data == 'remove_filter':
            await query.answer("Utilisez la commande /remove_filter <type> <valeur> dans le chat.", show_alert=True)
        elif data == 'set_amount':
            await query.answer()
            await query.message.reply_text("Merci d'entrer le montant de sniping en ETH :")
            return SET_AMOUNT
        else:
            await query.answer("Bouton non reconnu.", show_alert=True)

    # --- Conversation states ---
    async def receive_fid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        fid = update.message.text.strip()
        if not fid.isdigit():
            await update.message.reply_text("❌ Le FID doit être un nombre. Réessaie :")
            return ADD_FID
        WATCHED_FIDS.add(fid)
        await update.message.reply_text(f"✅ FID {fid} ajouté à la liste de surveillance !")
        return ConversationHandler.END

    async def receive_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = update.message.text.strip().upper()
        if not ticker.isalnum():
            await update.message.reply_text("❌ Le ticker doit être alphanumérique. Réessaie :")
            return ADD_TICKER
        WATCHED_TICKERS.add(ticker)
        await update.message.reply_text(f"✅ Ticker {ticker} ajouté à la liste de surveillance !")
        return ConversationHandler.END

    async def receive_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        address = update.message.text.strip()
        if not w3.is_address(address):
            await update.message.reply_text("❌ Adresse invalide. Réessaie :")
            return ADD_ADDRESS
        WATCHED_ADDRESSES.add(address.lower())
        await update.message.reply_text(f"✅ Adresse {address} ajoutée à la liste de surveillance !")
        return ConversationHandler.END

    async def receive_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            amount = float(update.message.text.strip())
            if amount <= 0:
                await update.message.reply_text("❌ Le montant doit être supérieur à 0. Réessaie :")
                return SET_AMOUNT
            self.snipe_amount = amount
            await update.message.reply_text(f"✅ Montant de sniping configuré à {amount} ETH")
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("❌ Montant invalide. Réessaie :")
            return SET_AMOUNT

def main():
    """Point d'entrée principal du bot"""
    # Créer l'application Telegram
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Créer l'instance du sniper
    sniper = ClankerSniper()
    
    # ConversationHandlers interactifs
    conv_fid = ConversationHandler(
        entry_points=[CallbackQueryHandler(sniper.handle_callback, pattern='^add_fid$')],
        states={ADD_FID: [MessageHandler(filters.TEXT & ~filters.COMMAND, sniper.receive_fid)]},
        fallbacks=[],
    )
    conv_ticker = ConversationHandler(
        entry_points=[CallbackQueryHandler(sniper.handle_callback, pattern='^add_ticker$')],
        states={ADD_TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, sniper.receive_ticker)]},
        fallbacks=[],
    )
    conv_address = ConversationHandler(
        entry_points=[CallbackQueryHandler(sniper.handle_callback, pattern='^add_address$')],
        states={ADD_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sniper.receive_address)]},
        fallbacks=[],
    )
    conv_amount = ConversationHandler(
        entry_points=[CallbackQueryHandler(sniper.handle_callback, pattern='^set_amount$')],
        states={SET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, sniper.receive_amount)]},
        fallbacks=[],
    )
    # Handlers classiques
    application.add_handler(conv_fid)
    application.add_handler(conv_ticker)
    application.add_handler(conv_address)
    application.add_handler(conv_amount)
    application.add_handler(CommandHandler("start", sniper.start))
    application.add_handler(CommandHandler("status", sniper.status))
    application.add_handler(CommandHandler("add_fid", sniper.add_fid))
    application.add_handler(CommandHandler("add_ticker", sniper.add_ticker))
    application.add_handler(CommandHandler("add_address", sniper.add_address))
    application.add_handler(CommandHandler("remove_filter", sniper.remove_filter))
    application.add_handler(CommandHandler("set_amount", sniper.set_snipe_amount))
    application.add_handler(CallbackQueryHandler(sniper.handle_callback))
    
    # Fonction pour démarrer le monitoring après l'initialisation du bot
    async def post_init(application: Application) -> None:
        """Start the monitoring task after the bot is initialized."""
        async def run_monitoring():
            while True:
                try:
                    await sniper.monitor_clanker()
                except Exception as e:
                    logger.error(f"Error in monitoring task: {e}")
                await asyncio.sleep(2)  # Attendre 2 secondes entre chaque vérification
        
        # Démarrer la tâche de monitoring
        asyncio.create_task(run_monitoring())
    
    # Ajouter le hook post_init
    application.post_init = post_init
    
    # Démarrer le bot
    application.run_polling()

if __name__ == "__main__":
    main() 