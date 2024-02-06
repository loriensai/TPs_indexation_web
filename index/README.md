# TP2 - Construction d'un index minimal

**Étudiante :** Lorie NOUZILLE

## Brève description

Ce projet permet de **créer un index web minimal** à partir d'une liste d'URLs fournie au format `json`, issue de la sortie d'un crawler. Il comprend l'extraction d'un champ spécifique des pages web, le processus de tokenisation de ce champ ainsi que leur prétraitement, suivi de la création de l'index web.

## Organisation de l'archive 

À la racine du projet, on retrouve les fichiers principaux du projet, ce sont ceux que vous devez lancer pour exécuter le code, on retrouve : 
*   **requirements.txt** : contient toutes les dépendances à installer ;
*   **main.py** : contient le code de création et de lancement des index webs.

L'archive contient également deux dossiers qui stockent les fichiers d'entrée et sortie : 
*   **donnees** : stocke le fichier `json` contenant la liste d'URLs servant de base à la création des index ; 
*   **resultats** : contient les métadonnées des documents traités ainsi que l'ensemble des index générés en fonction de différents paramètres tels que le choix du prétraitement et le type d'index (non positionnel ou positionnel).

## Installation des dépendances 

Avant de lancer les commandes qui vont suivre, veillez bien à vous déplacer dans le dossier `index`. 

Concernant les dépendances nécessaires au lancement de l'index, vous pouvez les installer avec la commande suivante : 

```
pip install -r requirements.txt
```

## Lancement du code 

Pour lancer le code de ce projet, il suffit de lancer la commande suivante : 

```
python3 main.py
```

## Construction des index web non positionnel et positionnel 

Cette section présente les étapes de construction des index web non positionnel et positionnel. Les index sont construits à partir d'un champ spécifique commun à tous les documents. En l'occurrence, ici, les titres et les contenus des pages ont été retenus et sont directement fournis dans le fichier `json`. Par conséquent, aucune étape d'extraction des champs des pages web n'était nécessaire. Il convient de noter que l'indexation se fait par champ, chaque champ ayant son propre index.   
L'idée principale de la construction des index web est de tokeniser le champ sélectionné pour tous les documents, puis de construire une liste inversée pour chaque token, associant ainsi chaque document à un token (document -> token) plutôt qu'un token à un document (token -> document).

La **différence entre un index non positionnel et positionnel** réside dans les informations collectées : l'index non positionnel associe l'identifiant d'un document à un token, tandis que l'index positionnel inclut également les positions des tokens et leur nombre d'apparitions au sein du document.    

Dans ce code, l'implémentation des index non positionnel et positionnel se fait simultanément. L'utilisateur précise uniquement les champs sur lesquels il souhaite construire les index. Il peut également préciser une option de prétraitement des données qui sera expliquée plus en détails dans la partie suivante. 

Les étapes qui vont suivre décrivent la logique suivie lors de l'implémentation des index web : 

1. Tout d'abord, le programme **récupère la liste des URLs fournies** au format `json`. Elle permet d'avoir directement, pour chaque page web, l'URL, le titre, le contenu et le texte situé dans la balise h1. 

2. Il **vérifie que les champs entrés par l'utilisateur** ont bien été founis dans le fichier `json`. Cette étape est assez spécifique à ce projet, dans l'idéal, il faudrait faire l'extraction des champs proposés par l'utilisateur des pages webs (par la lecture des fichiers HTML à télécharger à partir de l'URL fournie). Il faudrait tout de même que les champs proposés soient valides ou alors proposer une liste de possibilités à l'utilisateur.

3. Ensuite, les différents **champs retenus sont tokenisés et un traitement est appliqué en fonction de l'option choisie** par l'utilisateur. Un choix par défaut est implémenté.

4. Le programme collecte **quelques statistiques sur les documents** telles que le nombre de documents, le nombre de tokens global et par champ, le nombre de tokens unique global et par champ ainsi que la moyenne des tokens par champ. Ces informations sont ensuite stockées dans les fichiers json `metadata`. Dans le dossier `resultats`, deux fichiers de métadonnées sont stockées et dépendent du prétraitement appliqué sur les données. 

5. Enfin, des **index non positionnel et positionnel sont construits pour chaque champ** de la façon suivante : 
    *   Les index sont initialisés avec deux dictionnaires vides. 
    *   L'objectif ensuite est de créer une liste inversée pour chaque token (document -> token). Pour ce faire, le programme parcourt chaque liste de tokens pour le champ concerné et pour chaque document. Lors de ce parcourt, il explore ainsi chaque token de chaque liste. 
        *   Pour l'**index non positionnel** : Le programme initialise par défaut la clé du dictionnaire (l'index) avec le token et sa valeur par une liste vide. Ceci est réalisé uniquement si le token n'est pas présent dans l'index. Puis l'identifiant du document qui est en train d'être exploré est ajouté à la liste (s'il n'est pas déjà présent, pour éviter les doublons). 
        *   Pour l'**index positionnel** : Le programme initialise par défaut la clé du dictionnaire (l'index) avec le token et sa valeur par un dictionnaire, lui-même initialisé par défaut avec comme clé, l'identifiant du document en cours de traitement et comme valeur, le dictionnaire suivant : `{'positions': [], 'count': 0}`. Le programme vérifie ensuite que le token en cours de traitement pour le document n'a pas déjà été traité. Dans ce cas, le programme récupère la ou les positions du token parmi la liste de tokens du document et calcule le nombre d'occurrences du token. Celui-ci a donc été traité pour ce document. Pour ne pas le retraiter plusieurs fois, il est ajouté au dictionnaire des tokens déjà traités pour ce document. 
    *   Les **index crées sont ensuite exportés dans des fichiers `json`** portant des noms bien spécifiques en fonction de l'option de prétraitement des données appliquée et du type de l'index. 

## Prétraitement des données avancé 

La tokenisation et le traitement appliqué aux tokens constituent des choix importants lors de la création des index web. Le **prétraitement minimal par défaut consiste à effectuer une tokenisation avec un split sur les espaces et à mettre tous les tokens en minuscules (downcase)**. 

Cependant, cette méthode peut entraîner une séparation de tokens incorrecte. Certains tokens pourraient être rassemblés comme *contenu* et *contenu.* qui sont catégorisés comme étant des tokens différents à cause de la présence de la ponctuation ou encore *consulter* et *consultez* qui se rapportent au même verbe.         

Pour remédier à ces problèmes, le code propose un prétraitement des données plus avancé qui peut être activé en spécifiant l'option `stemming`. Ce prétraitement se déroule en 3 étapes :
*   Le document est d'abord **tokenisé avec un split sur les espaces** et la **ponctuation est supprimée**, puis chaque token est mis en minuscules (**downcase**).
*   La **suppression des stop words** : Les mots très courants et peu informatifs comme *de*, *la*, *les*, etc. sont supprimés. 
*   Enfin, un **stemmer** est appliqué pour réduire les tokens à leur forme racine, permettant ainsi de regrouper différentes variantes d'un même token. 

> Il est crucial de choisir le bon prétraitement, car le prétraitement avancé des données a par exemple permis de réduire considérablement la taille de l'index. D'autres options de prétraitement comme la lemmatisation pourraient également être envisagées.