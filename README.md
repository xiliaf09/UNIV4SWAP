# Clanker Sniper Bot

Bot Telegram pour le sniping automatique de tokens Clanker sur Base.

## Fonctionnalités

- Surveillance des nouveaux tokens Clanker
- Filtrage par FID, ticker et adresse Base
- Sniping automatique avec paramètres configurables
- Notifications Telegram en temps réel
- Interface utilisateur intuitive avec boutons

## Installation

1. Clonez le repository
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez le fichier `config.py` :
- Ajoutez votre token Telegram Bot
- Configurez votre adresse wallet Base et sa clé privée
- Ajustez les paramètres de sniping selon vos besoins

## Utilisation

1. Démarrez le bot :
```bash
python bot.py
```

2. Commandes disponibles :
- `/start` - Démarre le bot et affiche le menu principal
- `/status` - Affiche le statut actuel du bot
- `/add_fid <fid>` - Ajoute un FID à surveiller
- `/add_ticker <ticker>` - Ajoute un ticker à surveiller
- `/add_address <address>` - Ajoute une adresse Base à surveiller
- `/remove_filter <type> <value>` - Retire un filtre (fid/ticker/address)

## Configuration

Dans le fichier `config.py`, vous pouvez ajuster :
- Paramètres de sniping (slippage, gas limit, etc.)
- Filtres de liquidité et market cap
- Paramètres de notification

## Sécurité

- La clé privée du wallet est stockée uniquement dans le fichier de configuration
- Utilisez un wallet dédié pour le sniping
- Ne partagez jamais votre clé privée

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub. 