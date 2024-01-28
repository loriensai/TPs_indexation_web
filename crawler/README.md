# TP1 - Création d'un crawler 

Avant de lancer les commandes qui vont suivre, veillez bien à vous déplacer dans le dossier "crawler". 

## Installation des dépendances 

```
pip install -r requirements.txt
```

## Bonus : Base de données relationnelle

Lancement de la base de données via une image docker : 

```
sudo docker compose up -d
```

Lancement de la console `psql` pour requêter manuellement la table du jeu de données : 

```
psql -h localhost -U admin -d admin_db -p 5433
```

Commande pour voir toutes les tables créées : ```\dt```            
Quitter la console `psql` : ```\q```                 
 
Arrêt de la base de données :
```
sudo docker compose down 
``` 
