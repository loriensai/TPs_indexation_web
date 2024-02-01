import json
import numpy as np
import pandas as pd 
import nltk
from nltk.tokenize import regexp_tokenize

nltk.download('punkt')  # Téléchargez les modèles nécessaires


def index(liste_urls):

    # Lire le fichier json contenant les URLs générés par un crawler 
    df = pd.read_json(liste_urls, encoding="utf-8")

    # Tokeniser les titres 
    df["title_tokenize"] = df.apply(lambda row: regexp_tokenize(row['title'].lower(), r'\b\w+(?:\'\w+)?\b'), axis=1)

    df.to_csv('~/Téléchargements/mon_fichier.csv', index=False)

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
    with open("resultats/metadata.json", 'w') as fichier_json:
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
    with open('resultats/title.non_pos_index.json', 'w', encoding='utf-8') as fichier_json:
        json_str = json.dumps(index, ensure_ascii=False, sort_keys=True)
        json_str = json_str.replace('], "', '],\n "')
        fichier_json.write(json_str)


if __name__=="__main__":
    liste_urls = "donnees/crawled_urls.json"
    index(liste_urls)