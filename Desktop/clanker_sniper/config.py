import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ... autres variables de config ...

# Patch : notifications monitoring Clanker
NOTIFY_ON_NEW_TOKEN = False
NOTIFY_ON_ERROR = False

# Default gas settings for transactions
DEFAULT_GAS_LIMIT = 300000  # You can adjust this value as needed
DEFAULT_GAS_PRICE = 2  # Multiplier for current gas price, adjust as needed 