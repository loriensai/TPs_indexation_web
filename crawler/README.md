# TP1 - Création d'un crawler 

**Étudiante :** Lorie NOUZILLE

## Brève description

Ce projet **implémente un crawler en Python** avec comme point de départ une URL d'entrée unique (https://ensai.fr/). En analysant le contenu des pages déjà explorées, le crawler identifie de nouveaux liens à explorer. Le programme s'arrête après avoir exploré 50 URLs (nombre qui peut être modifié) ou en l'absence de nouveaux liens à explorer. 

Le crawler respecte deux principales règles de bonnes pratiques : 
*   Le crawler ne crawle pas un site web qui l'interdit. 
*   La politeness en attendant 5 secondes entre chaque appel et téléchargement de page. 

## Organisation de l'archive 

À la racine du projet, on retrouve les fichiers principaux du projet, ce sont ceux que vous devez lancer pour exécuter le code, on retrouve : 
*   **requirements.txt** : contient toutes les dépendances à installer ;
*   **docker-compose.yml** : permet de configurer le conteneur docker ;
*   **main.py** : contient le code de création et de lancement d'un crawler single-threaded ; 
*   **main_threads.py** : contient le code de création et de lancement d'un crawler multi-threaded. 

Cette archive se compose également de 3 dossiers nécessaires au lancement du projet et qui sont automatiquement appelés dans les fichiers main, on retrouve : 
*   **dao** : contient les codes pour créer et réaliser des opérations avec la base de données ;
*   **utils** : contient un objet URL pour réaliser des opérations simples sur une URL ; 
*   **resultats** : contient les fichiers .txt avec toutes les URLs trouvées par les crawlers. 

## Installation des dépendances 

Pour pouvoir exécuter ce projet, il vous faudra installer `docker` puisque ce projet utilise une image docker postgresql pour stocker les données en base de données. 

Avant de lancer les commandes qui vont suivre, veillez bien à vous déplacer dans le dossier `crawler`. 

Concernant les autres dépendances nécessaires, vous pouvez les installer avec la commande suivante : 

```
pip install -r requirements.txt
```

## Lancement du code 

Pour rappel, veuillez à vous placer dans le dossier `crawler` pour exécuter les commandes suivantes. 

Pour lancer le code de ce projet, il vous faut d'abord **lancer la base de données** via un conteneur et une image docker avec la commande suivante : 

```
sudo docker compose up -d
```

Pour **lancer le crawler single-threaded**, utilisez la commande : 

```
python3 main.py
```

Pour **lancer le crawler multi-threaded**, utilisez la commande : 

```
python3 main_threads.py
```

Les scripts python main sont conçus pour afficher l'état de la base de données à la fin de la compilation du code. Cependant, si vous souhaitez requêter la base de données manuellement, voici quelques commandes qui pourraient vous être utiles : 

*   Lancement de la console `psql` pour requêter manuellement la table du jeu de données : 

    ```
    psql -h localhost -U admin -d admin_db -p 5433
    ```             

    Si un mot de passe est demandé, entrez `password`.

*   Commande pour voir toutes les tables créées : ```\dt```     

*   Quitter la console `psql` : ```\q```                 
 
Enfin, pour arrêter la base de données, vous pouvez utiliser la commande suivante : 

```
sudo docker compose down 
``` 

Attention, cette commande arrêtera et supprimera le conteneur docker, l'image et les volumes associés. 

## Crawler single-threaded 

Cette section présente les étapes de construction du crawler single-threaded. L'objectif de ce dernier est de trouver des pages à explorer en analysant les balises des liens trouvées dans les documents précédemment explorés. Pour cela, le crawler single-threaded a pour point d'entrée une URL unique (https://ensai.fr). Il s'arrête lorsqu'il a trouvé et téléchargé 50 URLs ou s'il ne trouve plus de liens à explorer. D'autres règles sont à respecter, telles que la politeness (attendre 5 secondes entre chaque appel et entre deux téléchargements de pages), ne pas crawler un site qui l'interdit et explorer seulement 5 liens au maximum par page.

Les étapes qui vont suivre décrivent la logique suivie pour construire le crawler et ses règles : 

1. Tout d'abord, le crawler commence par **initialiser les variables** dont il a besoin : 
    *   La **frontier** qui est initialisée avec l'URL seed (https://ensai.fr) et qui va contenir la file d'attente des pages web à télécharger et à analyser. 
    *   Les **URLs visitées**, c'est-à-dire les URLs que le crawler a déjà téléchargé et analysé. Il est important de les stocker puisqu'on ne veut pas traiter une même URL plusieurs fois. 
    *   Les **sitemaps visités**, en effet dans cette version du crawler on considère (si c'est possible) qu'on va d'abord analyser les sitemaps d'une page web pour réduire les requêtes aux URLs. Il est important de les stocker également pour ne pas les analyser plusieurs fois. 
    *   Les **URLs avec lesquels on a rencontré des problèmes**, soit parce qu'on n'a pas l'autorisation de les crawler ou soit parce qu'on n'a pas réussi à les télécharger. Dans ce cas, on considère qu'on ne tentera pas de les visiter à nouveau et qu'on préférera se concentrer sur les autres URLs à explorer.

2. Ensuite, le crawler effectue une boucle `while` qui constitue la **condition d'arrêt** : il s'arrête après avoir trouvé et téléchargé 50 URLs ou lorsqu'il n'y a plus de liens à explorer.

3. Le crawler commence alors par **prendre la première URL de la frontier et analyse le fichier `robots.txt`** du site web. Celui-ci s'obtient en prenant l'URL racine du site web et en ajoutant `/robots.txt`. Par exemple, dans le cas du site web de l'ENSAI, il se trouve dans l'URL suivante : `https://ensai.fr/robots.txt`.                            
Ainsi, le crawler **vérifie s'il a l'autorisation de crawler l'URL et s'il peut récupérer les sitemaps de la page**. Il ajoute les sitemaps à la frontier s'ils n'ont pas encore été explorés. Les sitemaps sont des fichiers au format XML, on ne les comptera pas dans les URLs visitées (au format HTML). De plus, pour les sitemaps, le crawler n'applique pas la règle des 5 liens maximum par page.                    
Dans ce programme, le crawler considère par défaut qu'il n'a pas l'autorisation de crawler. En d'autres termes, il explore une page seulement s'il a l'autorisation explicite de le faire.                          
Comme le crawler effectue une requête à l'URL et qu'il analyse le contenu du fichier `robots.txt`, il respecte alors une **politeness** de 5 secondes. 

4.  Si <u>le crawler n'a pas l'autorisation de crawler</u>, il ajoute l'URL à la liste des URLs qui ont posé problème et reviens à l'étape 2. 

5.  Si <u>le crawler a l'autorisation de crawler</u>, il **télécharge la page**.            
    S'il échoue, il ajoute l'URL à la liste des URLs qui ont posé problème et revient à l'étape 2.            
    S'il réussit, il ajoute l'URL à la liste des URLs ou des sitemaps visités et **analyse le contenu** de la page en fonction de son type (HTML ou XML).                
    Si l'URL correspond à une page HTML, elle est également ajoutée ou mise à jour dans la base de données. 
    Le crawler **récupère ensuite au maximum 5 liens pour l'URL** en cours de traitement. Il faut que ces URLs n'aient pas déjà été visitées ou posées problème. Il faut également qu'elles ne soient pas déjà présentes dans la frontier.     
    Le crawler respecte ensuite une **politeness** qui correspond au temps de téléchargement de la page courante.           

6.  Le crawler retourne ensuite à l'étape 2 jusqu'à ce que la condition d'arrêt ne soit plus respectée. Dans ce cas, toutes les URLs trouvées et téléchargées sont stockées dans le fichier `crawled_webpages.txt` situé dans le dossier `resultats`, et l'état de la base de données est affiché.

**Focus sur les fonctions de la base de données**

La base de données contient un table `webpages` qui stocke l'identifiant de la page web et son URL, son âge et la date de la dernière visite par le crawler.

L'**âge de la page web** est initialisé à 0 lors de la première visite et augmente jusqu'à la visite suivante. 
Dans l'implémentation dans ce programme, l'âge est calculé en <u>minutes</u>.      

D'après la description détaillée du crawler, on pourrait penser qu'une page ne peut jamais être à nouveau visitée. Il faut alors imaginer que la base de données soit permanente et que le crawler s'arrête et peut alors être relancé et dans ce cas, il explorera des liens qui ont déjà été visités lors de son premier lancement, mais pas lors du lancement en cours.   

Avec les moyens dont nous disposons et le choix du calcul de l'âge en minutes, il est **difficile d'avoir une base de données mise à jour en temps réel**. C'est pourquoi, une mise à jour de la table est effectuée à la fin de l'étape 5 et permet de calculer le nouvel âge de toutes les pages explorées qui correspond à la différence en minutes de la date actuelle (du moment où la fonction mise à jour s'exécute) et la date de la dernière visite de la page. 

À l'étape 5, lorsqu'on **insère l'URL dans la base de données**, un programme s'occupe de vérifier d'abord si l'URL existe ou non. 
*   Si <u>elle n'existe pas</u>, elle est ajoutée dans la table avec un âge de 0 et une date de dernière visite qui est égale à la date actuelle, c'est-à-dire à la date où on fait l'insertion (et à quelques secondes près elle correspond à la date de téléchargement). 
*   Si <u>elle exite</u>, c'est-à-dire qu'elle a déjà été visitée par le crawler, son âge revient à 0 et la date de dernière visite est mise à jour. 

## Crawler multi-threaded 

Le crawler single-threaded a été présenté dans la partie précédente. Il explorait chaque URL présente dans la frontier de façon séquentielle jusqu'à une certaine condition d'arrêt. L'objectif du crawler multi-threaded est de **paralléliser l'exécution des tâches** en utilisant plusieurs threads qui traitent plusieurs URLs simultanément. Cette version du crawler permet de **diminuer considérablement le temps d'exécution** du programme. 

Pour construire un crawler multi-threaded, il est important de définir le nombre de threads à utiliser, ici 3 par défaut. Les variables d'initialisation (frontier, URLs et sitemaps visités et URLs qui posent problème) sont des variables globales, chaque thread peut les lire et les modifier. Pour ce faire, il est important de **définir un "verrou"** qui s'occupe d'empêcher plusieurs threads d'accéder et de modifier simultanément la même ressource. Ceci pourrait conduire à des résultats incohérents et à des erreurs. Ainsi, un thread peut lire et modifier les variables globales seulement si le verrou est libre, sinon il attend qu'il se libère avant de faire ses opérations (c'est ce qu'on peut appeler une section critique).

De plus, à l'initialisation de la frontier, il est important d'ajouter au départ plus d'une URL. Dans le cas inverse, on se retrouve dans une situation où un seul thread se lance sur l'URL seed et les autres threads, n'ayant pas d'URLs à traiter par la suite, vont simplement ne jamais se lancer. Pour pallier ce problème, avant de lancer les threads, on fait une première exploration des sitemaps que l'on ajoute à la frontier.

**Les threads sont ensuite lancés et effectuent la même tâche que le crawler single-threaded**. La seule différence repose sur leur accès aux variables globales régulé par le verrou.       

Lorsque la condition d'arrêt est obtenue par un thread, le programme attend que tous les autres threads finissent de traiter l'URL qui était en cours de traitement. 

Comme pour le crawler single-threaded, toutes les URLs trouvées et téléchargées sont stockées dans le fichier `crawled_webpages_threads.txt` situé dans le dossier `resultats`. Le crawler affiche également l'état de la base de données. 