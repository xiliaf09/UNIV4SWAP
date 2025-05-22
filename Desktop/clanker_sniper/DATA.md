# Données de Suivi - Clanker Sniper Bot

## 📊 FIDs Surveillés

### FIDs Importants
```python
WATCHED_FIDS = {
    "12345",  # Exemple FID
    "67890",  # Exemple FID
    # Ajouter vos FIDs ici
}
```

### FIDs par Catégorie
```python
# FIDs des Créateurs Populaires
POPULAR_CREATORS = {
    "12345",  # Créateur 1
    "67890",  # Créateur 2
}

# FIDs des Influencers
INFLUENCER_FIDS = {
    "11111",  # Influencer 1
    "22222",  # Influencer 2
}

# FIDs des Développeurs
DEVELOPER_FIDS = {
    "33333",  # Dev 1
    "44444",  # Dev 2
}
```

## 🎯 Tickers Surveillés

### Tickers Populaires
```python
WATCHED_TICKERS = {
    "PEPE",
    "WOJAK",
    "DOGE",
    # Ajouter vos tickers ici
}
```

### Tickers par Catégorie
```python
# Tickers Meme
MEME_TICKERS = {
    "PEPE",
    "WOJAK",
    "DOGE",
}

# Tickers Tech
TECH_TICKERS = {
    "AI",
    "GPT",
    "ML",
}

# Tickers Gaming
GAMING_TICKERS = {
    "GAME",
    "PLAY",
    "NFT",
}
```

## 🔍 Adresses Surveillées

### Adresses de Contrats
```python
WATCHED_ADDRESSES = {
    "0x123...",  # Adresse 1
    "0x456...",  # Adresse 2
    # Ajouter vos adresses ici
}
```

### Adresses par Type
```python
# Adresses des Créateurs
CREATOR_ADDRESSES = {
    "0x123...",  # Créateur 1
    "0x456...",  # Créateur 2
}

# Adresses des Pools
POOL_ADDRESSES = {
    "0x789...",  # Pool 1
    "0xabc...",  # Pool 2
}
```

## 📈 Historique des Snipes

### Snipes Réussis
```json
{
    "0x123...": {
        "token_name": "Example Token",
        "symbol": "EXT",
        "amount": "0.1",
        "timestamp": "2024-03-21T12:00:00Z",
        "profit": "0.05"
    }
}
```

### Snipes Échoués
```json
{
    "0x456...": {
        "token_name": "Failed Token",
        "symbol": "FTK",
        "error": "Insufficient liquidity",
        "timestamp": "2024-03-21T12:00:00Z"
    }
}
```

## 🔄 Filtres Actifs

### Filtres de Liquidité
```python
LIQUIDITY_FILTERS = {
    "min_liquidity": "1",  # ETH
    "max_liquidity": "100",  # ETH
    "min_holders": 10,
    "max_holders": 1000
}
```

### Filtres de Prix
```python
PRICE_FILTERS = {
    "min_price": "0.000001",  # ETH
    "max_price": "0.1",  # ETH
    "max_slippage": 100  # %
}
```

## 📊 Statistiques

### Performance
```python
PERFORMANCE_METRICS = {
    "total_snipes": 100,
    "successful_snipes": 80,
    "failed_snipes": 20,
    "total_profit": "5.0",  # ETH
    "average_profit": "0.05"  # ETH
}
```

### Temps de Réaction
```python
REACTION_TIMES = {
    "average_detection_time": "1.5",  # secondes
    "average_snipe_time": "2.0",  # secondes
    "best_reaction_time": "0.8"  # secondes
}
```

## 🔐 Configuration Sensible

### Paramètres de Gas
```python
GAS_SETTINGS = {
    "default_gas_limit": 300000,
    "default_gas_price": 2,  # Multiplicateur
    "max_gas_price": 100,  # Gwei
    "priority_fee": 1.5  # Gwei
}
```

### Paramètres de Snipe
```python
SNIPE_SETTINGS = {
    "default_amount": "0.1",  # ETH
    "max_amount": "1.0",  # ETH
    "min_amount": "0.01",  # ETH
    "max_slippage": 100  # %
}
```

## 📝 Notes Importantes

### Patterns de Succès
- Les tokens avec une liquidité initiale > 1 ETH ont plus de chances de succès
- Les créateurs avec un FID vérifié sont plus fiables
- Les tokens avec un nom/ticker mémorable ont plus de potentiel

### Patterns d'Échec
- Éviter les tokens avec une liquidité < 0.5 ETH
- Éviter les tokens avec un nombre de holders < 5
- Éviter les tokens avec un slippage > 50%

### Meilleures Pratiques
- Toujours vérifier la liquidité avant de sniper
- Surveiller les FIDs des créateurs populaires
- Maintenir une liste de tokens blacklistés
- Garder un historique des snipes pour analyse

## 🔄 Mise à Jour

Ce fichier doit être mis à jour régulièrement avec :
- Nouveaux FIDs à surveiller
- Nouveaux patterns de succès/échec
- Nouvelles adresses importantes
- Statistiques de performance
- Paramètres optimisés 