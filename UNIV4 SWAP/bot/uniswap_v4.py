import os
import json
import time
from web3 import Web3
from bot.base_web3 import get_web3, get_account
import logging
from eth_abi import encode_abi

# Adresse et ABI du Universal Router V4 sur Base
UNIVERSAL_ROUTER_ADDRESS = os.getenv("UNIVERSAL_ROUTER_ADDRESS", "0x6fF5693b99212Da76ad316178A184AB56D299b43")
UNIVERSAL_ROUTER_ABI = [
    {"inputs": [
        {"internalType": "bytes", "name": "commands", "type": "bytes"},
        {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"},
        {"internalType": "uint256", "name": "deadline", "type": "uint256"}
    ], "name": "execute", "outputs": [], "stateMutability": "payable", "type": "function"}
]
BASESCAN_TX_URL = "https://basescan.org/tx/"

# Constantes pour l'encodage des commandes/actions (à ajuster selon la doc officielle)
V4_SWAP_COMMAND = b"\x09"  # Commande V4_SWAP (exemple, à vérifier)
SWAP_EXACT_IN_SINGLE = 0x00  # Action code (à vérifier)
SETTLE_ALL = 0x01            # Action code (à vérifier)
TAKE_ALL = 0x02              # Action code (à vérifier)

# Adresse ETH natif (selon la doc Uniswap V4)
NATIVE_ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

async def buy_token_v4(token_address, amount_eth, max_fee_per_gas):
    w3 = get_web3()
    account = get_account()
    contract = w3.eth.contract(address=UNIVERSAL_ROUTER_ADDRESS, abi=UNIVERSAL_ROUTER_ABI)

    # 1. Préparer les actions (SWAP_EXACT_IN_SINGLE, SETTLE_ALL, TAKE_ALL)
    actions = bytes([SWAP_EXACT_IN_SINGLE, SETTLE_ALL, TAKE_ALL])

    # 2. Préparer le poolKey (simplifié, à adapter selon la pool réelle)
    # Pour ETH natif, currency0 = NATIVE_ETH_ADDRESS, currency1 = token_address
    # Les autres paramètres (fee, tickSpacing, hooks) doivent être déterminés selon la pool cible
    poolKey = (
        Web3.to_checksum_address(NATIVE_ETH_ADDRESS),
        Web3.to_checksum_address(token_address),
        3000,  # fee (exemple, à ajuster selon la pool)
        60,    # tickSpacing (exemple, à ajuster selon la pool)
        b""    # hooks (vide pour un swap simple)
    )

    # 3. Préparer les paramètres du swap (ExactInputSingleParams)
    amount_in = w3.to_wei(float(amount_eth), 'ether')
    min_amount_out = 1  # à ajuster selon la tolérance utilisateur
    deadline = int(time.time()) + 60

    # Encodage du paramètre swap (poolKey, zeroForOne, amountIn, amountOutMinimum, hookData)
    swap_params = encode_abi(
        [
            # poolKey struct
            "tuple(address,address,uint24,int24,bytes)",
            "bool",
            "uint128",
            "uint128",
            "bytes"
        ],
        [
            poolKey,
            True,  # zeroForOne: ETH -> token
            amount_in,
            min_amount_out,
            b""
        ]
    )

    # Encodage des paramètres SETTLE_ALL et TAKE_ALL
    settle_all_param = encode_abi(["address", "uint128"], [NATIVE_ETH_ADDRESS, amount_in])
    take_all_param = encode_abi(["address", "uint128"], [token_address, min_amount_out])

    # 4. Préparer inputs (un tableau de bytes)
    inputs = [swap_params, settle_all_param, take_all_param]

    # 5. Préparer commands (V4_SWAP)
    commands = V4_SWAP_COMMAND

    value = amount_in
    tx = contract.functions.execute(commands, inputs, deadline).build_transaction({
        'from': account.address,
        'value': value,
        'gas': 900_000,
        'maxFeePerGas': int(max_fee_per_gas),
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': w3.eth.chain_id,
    })
    signed = w3.eth.account.sign_transaction(tx, account.key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    basescan_url = BASESCAN_TX_URL + tx_hash.hex()
    logging.info(f"Swap ETH natif -> token envoyé via Universal Router : {tx_hash.hex()}")
    return tx_hash.hex(), basescan_url, "Swap ETH natif -> token en cours (Universal Router)" 