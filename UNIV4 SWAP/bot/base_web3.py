import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

BASE_RPC_URL = os.getenv("BASE_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

if not w3.is_connected():
    raise Exception("Web3 n'est pas connecté à Base. Vérifiez l'URL RPC.")

def get_web3():
    return w3

def get_account():
    return w3.eth.account.from_key(PRIVATE_KEY) 