# Contexte Technique - Clanker Sniper Bot

## 📡 API Clanker

### Endpoints Principaux
```python
CLANKER_API_URL = "https://api.clanker.com/v1"
```

#### 1. Liste des Tokens
- **Endpoint**: `/tokens`
- **Méthode**: GET
- **Paramètres**:
  - `page`: Numéro de page (pagination)
  - `sort`: "desc" pour les plus récents
- **Réponse**:
```json
{
  "data": [
    {
      "contract_address": "0x...",
      "name": "Token Name",
      "symbol": "TICKER",
      "requestor_fid": "12345",
      "created_at": "2024-03-21T12:00:00Z"
    }
  ]
}
```

### Structure des Données
- **Token**:
  - `contract_address`: Adresse du contrat sur Base
  - `name`: Nom du token
  - `symbol`: Ticker du token
  - `requestor_fid`: FID du créateur
  - `created_at`: Date de création

## 💰 Logique de Sniping

### 1. Surveillance Continue
```python
async def monitor_clanker(self):
    while True:
        try:
            # Appel API Clanker
            response = await client.get(f"{CLANKER_API_URL}/tokens")
            tokens = response.json()["data"]
            
            # Filtrage et sniping
            for token in tokens:
                if self.should_snipe(token):
                    await self.execute_snipe(token)
                    
        except Exception as e:
            logger.error(f"Error monitoring Clanker: {e}")
        
        await asyncio.sleep(2)  # Délai entre les vérifications
```

### 2. Filtrage des Tokens
```python
def should_snipe(self, token):
    # Vérification FID
    if WATCHED_FIDS and token['requestor_fid'] not in WATCHED_FIDS:
        return False
        
    # Vérification Ticker
    if WATCHED_TICKERS and token['symbol'].upper() not in WATCHED_TICKERS:
        return False
        
    # Vérification Adresse
    if WATCHED_ADDRESSES and token['contract_address'].lower() not in WATCHED_ADDRESSES:
        return False
        
    return True
```

### 3. Exécution du Sniping
```python
async def execute_snipe(self, token_address: str):
    # Préparation de la transaction
    amount_in = w3.to_wei(self.snipe_amount, 'ether')
    
    # Paramètres Uniswap V3
    params = {
        'tokenIn': WETH_ADDRESS,
        'tokenOut': token_address,
        'fee': 3000,  # 0.3%
        'recipient': WALLET_ADDRESS,
        'deadline': deadline,
        'amountIn': amount_in,
        'amountOutMinimum': 0,  # Slippage max
        'sqrtPriceLimitX96': 0
    }
    
    # Construction et envoi de la transaction
    tx = self.router.functions.exactInputSingle(params).build_transaction({
        'from': WALLET_ADDRESS,
        'value': amount_in,
        'gas': DEFAULT_GAS_LIMIT,
        'gasPrice': int(w3.eth.gas_price * DEFAULT_GAS_PRICE),
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS),
    })
```

## 🔄 Uniswap V3 Integration

### Router Configuration
```python
ROUTER_V3_ADDRESS = "0x5615CDAb10dc425a742d643d949a7F474C01abc4"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
```

### ABI Minimal
```python
ROUTER_V3_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]
```

## 🔐 Gestion des Variables Sensibles

### Variables d'Environnement
```python
# .env
TELEGRAM_BOT_TOKEN=your_telegram_token
WALLET_ADDRESS=your_base_wallet
PRIVATE_KEY=your_private_key
```

### Configuration
```python
# config.py
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
```

## 📊 Gestion des Filtres

### Structure des Filtres
```python
class ClankerSniper:
    def __init__(self):
        self.seen_tokens: Set[str] = set()
        self.active_snipes: Dict[str, Dict] = {}
        self.snipe_amount = DEFAULT_SNIPE_AMOUNT
```

### Persistance des Filtres
```python
def load_seen_tokens(self):
    try:
        if os.path.exists('seen_tokens.json'):
            with open('seen_tokens.json', 'r') as f:
                self.seen_tokens = set(json.load(f))
    except Exception as e:
        logger.error(f"Error loading seen tokens: {e}")
```

## 🔄 Workflow Complet

1. **Initialisation**
   - Chargement des variables d'environnement
   - Configuration Web3 et Uniswap
   - Chargement des filtres existants

2. **Surveillance**
   - Appel périodique à l'API Clanker
   - Filtrage des nouveaux tokens
   - Vérification des critères de sniping

3. **Sniping**
   - Vérification du solde ETH
   - Construction de la transaction
   - Envoi et confirmation
   - Notification du résultat

4. **Gestion des Erreurs**
   - Logging détaillé
   - Notifications Telegram
   - Reprise automatique

## 📈 Optimisations Possibles

1. **Performance**
   - Mise en cache des réponses API
   - Optimisation des délais de vérification
   - Gestion des rate limits

2. **Sécurité**
   - Vérification des contrats avant sniping
   - Limites de montant
   - Timeout des transactions

3. **Fonctionnalités**
   - Support multi-wallets
   - Analyse de liquidité
   - Stop-loss automatique

## 🔍 Dépannage

### Erreurs Courantes
1. **Transaction Failed**
   - Vérifier le solde ETH
   - Vérifier le gas price
   - Vérifier la validité du token

2. **API Errors**
   - Vérifier la connexion
   - Vérifier les rate limits
   - Vérifier le format des données

3. **Web3 Errors**
   - Vérifier la connexion RPC
   - Vérifier les nonces
   - Vérifier les signatures

## 📚 Ressources

- [Documentation Clanker API](https://docs.clanker.com)
- [Documentation Uniswap V3](https://docs.uniswap.org)
- [Documentation Base](https://docs.base.org)
- [Documentation Web3.py](https://web3py.readthedocs.io) 