import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Base Configuration
BASE_RPC_URL = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Sniper Settings
DEFAULT_SNIPE_AMOUNT = float(os.getenv('DEFAULT_SNIPE_AMOUNT', '0.1'))  # in ETH
DEFAULT_SLIPPAGE = float(os.getenv('DEFAULT_SLIPPAGE', '100.0'))  # 100% max
GAS_LIMIT = int(os.getenv('GAS_LIMIT', '300000'))
GAS_PRICE = float(os.getenv('GAS_PRICE', '1.5'))  # in Gwei

# Clanker API URL
CLANKER_API_URL = "https://www.clanker.world/api"

# Filter Settings
MIN_LIQUIDITY = float(os.getenv('MIN_LIQUIDITY', '0.1'))  # in ETH
MIN_MARKET_CAP = float(os.getenv('MIN_MARKET_CAP', '0.1'))  # in ETH
MIN_HOLDERS = int(os.getenv('MIN_HOLDERS', '1'))

# Watched FIDs, Tickers, and Addresses
WATCHED_FIDS = set()
WATCHED_TICKERS = set()
WATCHED_ADDRESSES = set()

# Notification Settings
NOTIFY_NEW_TOKENS = True
NOTIFY_SNIPES = True
NOTIFY_ERRORS = True 