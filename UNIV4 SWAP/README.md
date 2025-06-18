# Uniswap V4 Swap Telegram Bot

Ce bot Telegram permet d'acheter n'importe quel token compatible Uniswap V4 sur la blockchain Base via une simple commande Telegram.

## Fonctionnalités principales
- Achat de tokens via la commande `/buyv4 <token_address> <amount_eth> <max_fee_per_gas>`
- Vérification de la liquidité et de l'existence de la pool Uniswap V4
- Gestion de l'approbation du token d'entrée (ETH natif ou WETH)
- Affichage du hash de la transaction et d'un lien vers Basescan
- Exploitation des nouveautés Uniswap V4 : hooks, singleton, flash accounting, support ETH natif

## Stack technique
- Python 3.10+
- python-telegram-bot
- web3.py
- Déploiement Railway

## Configuration
1. Cloner le repo
2. Copier `.env.example` en `.env` et remplir les variables nécessaires
3. Installer les dépendances : `pip install -r requirements.txt`
4. Lancer le bot : `python main.py`

## Déploiement Railway
- Toutes les variables sensibles doivent être configurées dans Railway (voir `.env.example`).

## Structure du projet
```
/univ4swap-bot/
│
├── bot/
│   ├── __init__.py
│   ├── handlers.py
│   ├── uniswap_v4.py
│   ├── base_web3.py
│   └── utils.py
├── requirements.txt
├── README.md
├── .env.example
└── main.py
```

## Sécurité
Aucune donnée sensible ne doit être hardcodée dans le code source. Utilisez les variables d'environnement.

## À venir
- Documentation détaillée des commandes
- Support d'autres fonctionnalités Uniswap V4 