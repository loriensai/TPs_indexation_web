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


def index(liste_urls, langage='french', option=None):

    # Lire le fichier json contenant les URLs générés par un crawler 
    df = pd.read_json(liste_urls, encoding="utf-8")

    # Tokeniser les titres 
    if option is None : 
        df["title_tokenize"] = df.apply(lambda row: data_processing_simple(row['title']), axis=1)
    elif option=="stemming":
        df["title_tokenize"] = df.apply(lambda row: data_processing_complexe(row['title'], option, langage), axis=1)
    else : 
        raise ValueError(f"La valeur '{option}' n'est pas prise en charge. Choisissez parmi None ou stemming.")

    # Statistiques sur les documents

    metadonnees = {}

    # Nombre de documents 
    metadonnees["nombre_documents"] = int(len(df))
    # Nombre total de tokens pour le champs 'title'
    metadonnees["nombre_tokens_title"] = int(df['title_tokenize'].apply(lambda x: len(x)).sum())
    # Nombre total de tokens unique pour le champ 'title'
    metadonnees["nombre_tokens_unique_title"] = int(df['title_tokenize'].explode().nunique())
    # Moyenne des tokens par titre des documents 
    metadonnees["moyenne_tokens_title"] = int(round(df['title_tokenize'].apply(lambda x: len(x)).mean(),0))

    print(metadonnees)

    # Exporter les métadonnées dans un fichier json 
    nom_metadonnees = f"resultats/metadata.json" if option is None else f"resultats/{option}.metadata.json"
    with open(nom_metadonnees, 'w') as fichier_json:
        json.dump(metadonnees, fichier_json, indent=4)
    
    # Construction de l'index 
    
    index = {} # Initialisation de l'index 

    # Création d'une liste inversée pour chaque token 
    for id, tokens in enumerate(df['title_tokenize']):
        for token in tokens :
            if token in index:
                index[token].append(id)
            else:
                index[token] = [id]
    
    # Exporter la chaîne formatée vers un fichier
    nom_index = f"resultats/title.non_pos_index.json" if option is None else f"resultats/{option}.title.non_pos_index_json"
    with open(nom_index, 'w', encoding='utf-8') as fichier_json:
        json_str = json.dumps(index, ensure_ascii=False, sort_keys=True)
        json_str = json_str.replace('], "', '],\n "')
        fichier_json.write(json_str)


if __name__=="__main__":
    # Liste des URLs générer par un crawler
    liste_urls = "donnees/crawled_urls.json"
    # Data processing simple
    index(liste_urls)
    # Data processing avancé
    index(liste_urls, option="stemming")