import json
import pandas as pd 
import nltk
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


# Deux prochaines lignes à compiler seulement si les modèles ne sont pas déjà téléchargés
# nltk.download('punkt') 
# nltk.download('stopwords')


def data_processing_simple(doc:str):
    return doc.lower().split()


def data_processing_complexe(doc:str, option, langage):

    # Étape 1: Minuscules et suppression de la ponctuation
    tokens = regexp_tokenize(doc.lower(), r'\b\w+\b')

    # Étape 2: Suppression des stop words
    stop_words = set(stopwords.words(langage))
    tokens_filtres = [token for token in tokens if token not in stop_words]

    # Étape 3: Appliquer l'option si elle est précisée 
    if option=="stemming":
        stemmer = SnowballStemmer(langage)
        res = [stemmer.stem(token) for token in tokens_filtres]
    else:
        res = tokens_filtres
    return res

def export_json(nom_fichier, dictionnaire, replace=None):
    with open(nom_fichier, 'w', encoding='utf-8') as fichier_json:
        json_str = json.dumps(dictionnaire, ensure_ascii=False, sort_keys=True)
        if replace : 
            json_str = json_str.replace(replace[0], replace[1])
        fichier_json.write(json_str)

def index(liste_urls, champs=['title'], option=None, langage='french'):

    # Lire le fichier json contenant les URLs générés par un crawler 
    df = pd.read_json(liste_urls, encoding="utf-8")

    # Tokeniser les titres 
    for col in champs : 
        if option is None : 
            df[f"{col}_tokenize"] = df.apply(lambda row: data_processing_simple(row[col]), axis=1)
        elif option=="stemming":
            df[f"{col}_tokenize"] = df.apply(lambda row: data_processing_complexe(row[col], option, langage), axis=1)
        else : 
            raise ValueError(f"La valeur '{option}' n'est pas prise en charge. Choisissez parmi None ou stemming.")

    # Statistiques sur les documents

    metadonnees = {}

    # Nombre de documents 
    metadonnees["nombre_documents"] = int(len(df))
    for col in champs : 
        # Nombre total de tokens pour le champs 'title'
        metadonnees[f"nombre_tokens_{col}"] = int(df[f'{col}_tokenize'].apply(lambda x: len(x)).sum())
        # Nombre total de tokens unique pour le champ 'title'
        metadonnees[f"nombre_tokens_unique_{col}"] = int(df[f'{col}_tokenize'].explode().nunique())
        # Moyenne des tokens par 'title' des documents 
        metadonnees[f"moyenne_tokens_{col}"] = int(round(df[f'{col}_tokenize'].apply(lambda x: len(x)).mean(),0)) 

    print(metadonnees)

    # Exporter les métadonnées dans un fichier json 
    nom_metadonnees = f"resultats/metadata.json" if option is None else f"resultats/{option}.metadata.json"
    export_json(nom_metadonnees, metadonnees, [', "', ',\n "'])
    
    # Construction des index (non positionnel et positionnel)

    # Création d'une liste inversée pour chaque token 
    for col in champs : 

        index_non_pos = {} # Initialisation de l'index non positionnel
        index_pos = {}     # Initialisation de l'index positionnel

        for id_doc, liste_tokens in enumerate(df[f'{col}_tokenize']):

            processed_tokens = set() 
            for token in liste_tokens :

                # Index non positionnel
                index_non_pos.setdefault(token, [])
                if id_doc not in index_non_pos[token]:
                    index_non_pos[token].append(id_doc)

                # Index positionnel
                index_pos.setdefault(token, {})
                index_pos[token].setdefault(str(id_doc), {'positions': [], 'count': 0})
                if token not in processed_tokens:

                    # Obtenir tous les indices où le token apparaît dans la liste des tokens
                    positions = [i for i, t in enumerate(liste_tokens) if t == token]
                    index_pos[token][str(id_doc)]['positions'].extend(positions)
                    index_pos[token][str(id_doc)]['count'] += len(positions)

                    # Ajouter le token à la liste des tokens déjà traités
                    processed_tokens.add(token)
        
        # Exporter les index vers des fichiers json
        nom_index = f"resultats/{col}.non_pos_index.json" if option is None else f"resultats/{option}.{col}.non_pos_index.json"
        export_json(nom_index, index_non_pos, ['], "', '],\n "'])
        nom_index = f"resultats/title.pos_index.json" if option is None else f"resultats/{option}.{col}.pos_index.json"
        export_json(nom_index, index_pos, ['}}, "', '}},\n "'])


if __name__=="__main__":
    # Liste des URLs générer par un crawler
    liste_urls = "donnees/crawled_urls.json"
    # Data processing simple
    index(liste_urls, champs=['title'])
    # Data processing avancé
    index(liste_urls, champs=['title', 'content'], option="stemming")