import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Telegram
TELEGRAM_BOT_TOKEN = "7643873228:AAES7SlB7Oa3apyO09O5V2JeeBUue01QzUw"

# Configuration Clanker
CLANKER_API_URL = "https://www.clanker.world/api"

# Configuration Base
BASE_RPC_URL = "https://mainnet.base.org"
WALLET_ADDRESS = "0x8840Ce566511F49Fc4bc381F4d54EB3BCDD11AB1"
PRIVATE_KEY = "0x0cb9dd4812e597899e8fd8d37829cefce8ae318507d713ac2fee6b842bd98086"

# Configuration du Sniper
DEFAULT_SLIPPAGE = 100.0  # 100% max
DEFAULT_GAS_LIMIT = 500000
DEFAULT_GAS_PRICE = 1.1  # Multiplicateur du prix du gas
DEFAULT_SNIPE_AMOUNT = 0.1  # Montant par défaut en ETH

# Paramètres de filtrage
MIN_LIQUIDITY = 0.1  # ETH
MAX_MARKET_CAP = 1000000  # USD
MIN_HOLDERS = 10

# Liste des FIDs à surveiller
WATCHED_FIDS = set()

# Liste des tickers à surveiller
WATCHED_TICKERS = set()

# Liste des adresses Base à surveiller
WATCHED_ADDRESSES = set()

# Configuration des notifications
NOTIFY_ON_NEW_TOKEN = True
NOTIFY_ON_SNIPE = True
NOTIFY_ON_ERROR = True 