import json
import pandas as pd 
import nltk
from nltk.corpus import stopwords
from functools import reduce
from operator import and_, or_
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer


def data_processing_simple(doc:str)->list:
    """ Tokenisation d'un document avec un prétraitement minimal

    Le prétraitement comprend : 
        - une tokenization du document avec un split sur les espaces ; 
        - la conversion des tokens en minuscules (downcase).

    Args:
        doc (str): document à tokeniser 

    Returns:
        list: document tokenisé avec le prétraitement minimal
    """
    return doc.lower().split()


def ranking_lineaire(id_docs, infos_doc, documents, req_tokens):
    scores = {}

    # Calculer l'IDF pour appliquer un poids plus important aux tokens qui ont du sens par rapport aux stop words
    vectorizer = TfidfVectorizer(vocabulary=req_tokens)
    vectorizer.fit(documents['content'])
    idf_scores = vectorizer.idf_

    # Variable 1 : Importance sur le compte des tokens 
    for doc in id_docs:
        for token in req_tokens : 

            # Récupérer le poids du token calculé avec l'IDF
            poids = idf_scores[vectorizer.vocabulary_[token]]

            scores.setdefault(doc, 0)
            
            score_count_title = 10 * poids * infos_doc['title'][token][doc]['count']
            score_count_content = 5 * poids * infos_doc['content'][token][doc]['count']

            scores[doc] += score_count_title + score_count_content
    
    # Variable 2 : Score bm25
    for doc in id_docs:
        content_doc = documents[documents.apply(lambda x: x['id'] == int(doc), axis=1)]
        
        # Titre
        corpus = content_doc['title'].apply(lambda x: data_processing_simple(x))
        bm25 = BM25Okapi(corpus)
        score_bm25_title = 10 * float(bm25.get_scores(req_tokens))
        
        # Corpus 
        corpus = content_doc['content'].apply(lambda x: data_processing_simple(x))
        bm25 = BM25Okapi(corpus)
        score_bm25_content = 5 * float(bm25.get_scores(req_tokens))

        scores[doc] += score_bm25_title + score_bm25_content

    # Trier les scores par ordre décroissant 
    scores_tries = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return scores_tries

def reponse_requete(requete, type_filtre:str='et'):

    # Vérification du type de l'entrée
    if type_filtre not in ['et', 'ou']:
        raise ValueError("Le type de filtre choisi est incorrect. Veuillez-choisir entre 'et' et 'ou'.")

    # Importer les documents 
    documents = pd.read_json("donnees/documents.json", encoding="utf-8")

    # Importer l'index des titres 
    with open("donnees/title_pos_index.json", 'r', encoding="utf-8") as fichier_json:
        df_title = json.load(fichier_json)

    # Importer l'index des contenus 
    with open("donnees/content_pos_index.json", 'r', encoding="utf-8") as fichier_json:
        df_content = json.load(fichier_json)

    # Tokeniser la requête avec le même data processing que celui appliqué aux documents
    req_tokens = data_processing_simple(requete)

    # Récupérer la liste des identifiants des documents où les tokens apparaissent
    tokens_docs = {}
    for df in [df_title, df_content]:
        for token, doc in df.items():
            if token in req_tokens:
                tokens_docs.setdefault(token, []).extend(list(doc.keys()))
    
    # Récupérer les identifiants des documents selon le type de filtre 
    # "ET" : Les documents ont tous les tokens de la requête
    if type_filtre=="et" : 
        id_doc_tokens_req = list(reduce(and_, (set(v) for v in tokens_docs.values())))
    # "OU" : Les documents ont au moins un token de la requête
    elif type_filtre=="ou": 
        id_doc_tokens_req = list(reduce(or_, (set(v) for v in tokens_docs.values())))

    # Stocker les informations des tokens dans les documents restants
    infos_doc = {}
    for col in ['title', 'content']: 
        infos_doc[col] = {}
        index = df_title if col=='title' else df_content
        for token in req_tokens : 
            for id_doc in id_doc_tokens_req : 
                infos_doc[col].setdefault(token, {}).setdefault(str(id_doc), {'positions': [], 'count': 0})
                if (token in index) and (id_doc in index[token]) :
                    infos_doc[col][token][id_doc] = index[token][id_doc]

    # Appliquer la fonction de ranking linéaire pour ordonner les documents restants 
    scores_doc = ranking_lineaire(id_doc_tokens_req, infos_doc, documents, req_tokens)
    
    # Collecte des résultats du ranking avec les informations sur les documents et les pages
    resultat = {}
    resultat['nombre_documents_index'] = int(len(documents))
    resultat['nombre_documents_apres_filtre'] = len(id_doc_tokens_req)
    resultat['ranking'] = {}
    pd.set_option('display.max_colwidth', None) # Configuration de l'affichage pour éviter la troncature des titres et des URLs
    for i, (doc, score) in enumerate(scores_doc) : 
        infos = documents[documents.apply(lambda x: x['id'] == int(doc), axis=1)]
        resultat['ranking'][i] = {
            'titre': infos['title'].values[0],
            'url': infos['url'].values[0],
            'score': score
        }
        
    # Exporter les résultats dans un fichier json 
    with open(f'resultats/results_{type_filtre}.json', 'w', encoding='utf-8') as fichier_json:
        json_str = json.dumps(resultat, ensure_ascii=False)
        json_str = json_str.replace(', "', ',\n "')
        fichier_json.write(json_str)

if __name__=="__main__":
    requete = "pass sanitaire covid-19"
    reponse_requete(requete, "et")
    reponse_requete(requete, "ou") 