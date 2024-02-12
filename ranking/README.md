# TP3 - Expansion de requête et ranking 

**Étudiante :** Lorie NOUZILLE

## Brève description

Ce projet permet de **répondre à une requête donnée** par un utilisateur en sélectionnant les documents pertinents pour la requête et en les classant. Cela est réalisé grâce à l'utilisation d'une **fonction de ranking** qui évalue chaque document et lui attribue un score en fonction de sa pertinence par rapport à la requête donnée.

## Organisation de l'archive 

À la racine du projet, on retrouve les fichiers principaux du projet, ce sont ceux que vous devez lancer pour exécuter le code, on retrouve : 
*   **requirements.txt** : contient toutes les dépendances à installer ;
*   **main.py** : contient le code qui permet de traiter la requête et d'ordonnancer les résultats qui s'y réfèrent. 

L'archive contient également deux dossiers qui stockent les fichiers d'entrée et sortie : 
*   **donnees** : stocke des fichiers `json` contenant des informations sur les documents et les deux index positionnels crées à partir du titre et du contenu des documents ; 
*   **resultats** : contient l'ordonnancement des résultats retenus pour des requêtes de type *et* et *ou*.

## Installation des dépendances 

Avant de lancer les commandes qui vont suivre, veillez bien à vous déplacer dans le dossier `ranking`. 

Concernant les dépendances nécessaires au lancement du code, vous pouvez les installer avec la commande suivante : 

```
pip install -r requirements.txt
```

## Lancement du code 

Pour lancer le code de ce projet, il suffit de lancer la commande suivante : 

```
python3 main.py
```

## Traitement d'une requête et ordonnancement des résultats

Cette section présente les étapes mises en place afin de répondre à une requête d'un utilisateur notamment en sélectionnant et en classant un ensemble de documents pertinents pour la requête donnée. Il convient de noter que **l'utilisateur a la possibilité de choisir entre deux types de requêtes** : 
*   *et* : les documents sélectionnés ont tous les tokens de la requête.
*   *ou* : les documents sélectionnés contiennent au moins un token de la requête. 
Ainsi, une requête de type *et* est beaucoup plus restrictive qu'une requête de type *ou*. Dans certains cas, il se peut même qu'aucun document ne puisse répondre à la requête, notamment lorsque celle-ci contient beaucoup de tokens. 

Les étapes suivantes détaillent donc la logique suivie pour traiter une requête et classer les résultats : 

1. Tout d'abord, le programme **vérifie qu'il est capable de prendre en charge le type de requête donné** par l'utilisateur. Dans le cas où ce dernier spécifierait autre chose que *et* ou *ou*, le programme lève une erreur. 

2. Ensuite, il **importe les informations sur les documents** à savoir l'URL du document, son identifiant, le titre et le contenu du document extrait de la page HTML. Il **importe également les deux index positionnels créés en amont à partir du titre et du contenu des documents**.        
Pour ce code, les index utilisés sont ceux qui ont été fournis et ne sont pas issus du programme implémenté dans le dossier `index`. 

3. À présent, il convient de **transformer la requête en utilisant la même transformation que celle appliquée sur les documents** lors de la construction des index positionnels. Pour les index founis, le prétraitement appliqué consiste à effectuer une tokenisation avec un split sur les espaces et à mettre tous les tokens en minuscules (downcase). C'est donc ce qui a été appliqué à la requête. 

4. La prochaine étape consiste à **sélectionner les documents pertinents pour répondre à la requête en fonction du type de requête** choisi par l'utilisateur. 
    * Le programme sélectionne d'abord la liste des identifiants des documents où les tokens apparaissent, que ce soit dans le titre et/ou dans le contenu de la page. Il obtient un dictionnaire avec la structure suivante : `{'token' : [identifiants des documents]}`.
    * Il stocke ensuite dans une liste les identifiants des documents qui contiennent tout ou une partie des tokens de la requête en fonction du type de requête choisi. 

5. Le programme **récupère ensuite à toutes les informations qu'il possède sur les tokens et leurs informations dans les documents restants**, à savoir leur nombre d'occurrences et leurs positions dans le document. Il différencie les informations relatives au titre et celles relatives au contenu. 

6. Ces informations sont ensuite transmises à la **fonction de ranking qui attribue un score à chaque document afin de les classer**. Plus le score est élevé et plus le document est pertinent pour la requête donnée. Le calcul de ce score est détaillé juste après. Les documents sont ensuite triés par ordre décroissant de score. 

7. Enfin, le programme **stocke dans un fichier `json` les informations issues du traitement de la requête** à savoir :
    * le nombre de documents total sur lequel se base le traitement ;
    * le nombre de documents ayant survécu au filtre ;
    * la liste des documents classés par ordre de pertinence pour répondre à la requête. Chaque document est présenté avec son titre, son URL et le score attribué par la fonction de ranking. 

## Fonction de ranking 

Comme expliqué précédemment, la fonction de ranking permet d'attribuer un score à chaque document afin de les classer par ordre de pertinence. En réalité, **le score est composé de plusieurs scores auxquels on attribue une importance plus ou moins forte**.

Pour l'implémentation de cette fonction, il a été décidé de la calculer en fonction de deux paramètres : 
1. Le **nombre d'occurrences du token** dans le document (titre et contenu).
2. Le **score bm25** qui mesure la pertinence du champ du document par rapport à la requête. 

Les scores de ces deux paramètres sont calculés spécifiquement pour les champs titre et contenu puisqu'on ne leur accorde pas le même degré d'importance. En effet, ici **il a été considéré que le score avait une importance plus forte pour les titres par rapport au contenu** des documents.  En général, les documents les plus pertinents observés en premier via un moteur de recherche sont ceux qui ont les tokens de la requête directement dans leur titre.

De plus, **un poids (et donc un score) plus important est accordé aux tokens qui ont du sens par rapport aux stop words**. En d'autres termes, l'IDF (inverse document frequency) est calculé sur l'ensemble des contenus des documents afin d'attribuer un poids à chaque token de la requête. L'IDF diminue le poids des termes qui apparaissent très fréquemment et augmente le poids des termes qui apparaissent rarement. Ainsi, les stopwords de la requête auront beaucoup moins de poids. Ceci évite donc, notamment dans le cas des requêtes de type *ou*, d'avoir des documents extrêmement bien classés pour la requête alors qu'ils contiennent en réalité un nombre conséquent de stop words de la requête et très peu ou pas du tout les autres mots-clés de la requête. 

La score calculé pour chaque document (et en sommant sur chaque token) peut se résumer ainsi : 

```math
\text{Score} \leftarrow 10 \times \text{idfScore(token)} \times \text {nbOccurrencesTitre(token)} 
```
```math
+ 5 \times \text{idfScore(token)} \times \text{nbOccurrencesContenu(token)} 
```
```math
+ 10 \times \text{bm25(requête, titre)} 
```
```math
+ 5 \times \text{bm25(requête, contenu)}
```

> Une multitude d'approches pourraient être envisagées pour calculer le score des documents, il est donc important de réfléchir aux fonctions de scoring qui le composent pour que le score soit le plus pertinent possible. Pour aller plus loin, il serait aussi intéressant d'évaluer la pertinence des résultats obtenus afin de voir quelles améliorations pourraient être apportées et comment. 