import json
import numpy as np
import pandas as pd 
import nltk
from nltk.tokenize import word_tokenize
from functools import reduce
from operator import and_, or_

def ranking(requete):

    # Importer les documents 
    df = pd.read_json("donnees/documents.json", encoding="utf-8")
    
    # Importer l'index des titres 
    with open("donnees/title_pos_index.json", 'r', encoding="utf-8") as fichier_json:
        df_title = json.load(fichier_json)

    # Importer l'index des contenus 
    with open("donnees/content_pos_index.json", 'r', encoding="utf-8") as fichier_json:
        df_content = json.load(fichier_json)

    # Tokeniser la requête avec un split sur les espaces + downcase 
    req_tokens = [token.lower() for token in word_tokenize(requete)]
    print(req_tokens)

    # Récupérer la liste des documents où les tokens apparaissent
    tokens_docs = {}
    tokens_docs_infos = {}

    for df in [df_title, df_content]:
        for token, doc in df.items():
            if token in req_tokens:
                if token in tokens_docs:
                    tokens_docs_infos[token].extend(list(doc.items()))
                    tokens_docs[token].extend(list(doc.keys()))
                else:
                    tokens_docs_infos[token] = list(doc.items())
                    tokens_docs[token] = list(doc.keys())

    # Récupérer les identifiants des documents qui ont tous les tokens de la requête 
    id_tokens_communs = list(reduce(and_, (set(v) for v in tokens_docs.values())))

    print("doc : ",id_tokens_communs)

    # Stocker les informations sur les documents restants et les tokens 
    print(tokens_docs_infos)

    # Créer la fonction de ranking linéaire pour ordonner les documents restants 

    pass

if __name__=="__main__":
    requete = "erreurs statistiques classiques"
    ranking(requete)