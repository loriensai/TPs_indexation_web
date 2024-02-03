import json
import pandas as pd 
import nltk
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


# Deux prochaines lignes à compiler seulement si les modèles ne sont pas déjà téléchargés
nltk.download('punkt') 
nltk.download('stopwords')


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

def data_processing_complexe(doc:str, option:str, langage:str)->list:
    """ Tokenisation d'un document avec un prétraitement avancé

    Le prétraitement comprend : 
        - une tokenization du document avec un split sur les espaces 
          et qui ignore la ponctuation et d'autres caractères non-alphanumériques ;
        - la conversion des tokens en minuscules (downcase) ;
        - la suppression des stop words ;
        - l'application d'un stemmer (si précisé).

    Args:
        doc (str): document à tokeniser
        option (str): option supplémentaire à appliquer au prétraitement (stemming ou None)
        langage (str): langage utilisé pour repérer les stop words 

    Returns:
        list: document tokenisé avec le prétraitement avancé
    """

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

def export_json(nom_fichier:str, dictionnaire:dict, replace:list=None):
    """ Exportation des données dans un fichier json

    Args:
        nom_fichier (str): nom du fichier json
        dictionnaire (dict): dictionnaire des données à exporter 
        replace (list, optional): opération de substitution de texte dans la chaîne pour un affichage plus lisible dans le json 
                                  Valeur par défaut : None.                                
    """
    with open(nom_fichier, 'w', encoding='utf-8') as fichier_json:
        json_str = json.dumps(dictionnaire, ensure_ascii=False, sort_keys=True)
        if replace : 
            json_str = json_str.replace(replace[0], replace[1])
        fichier_json.write(json_str)

def index(liste_urls:str, champs:list=['title'], option:str=None, langage:str='french'):
    """ Index non positionnel et positionnel

    Args:
        liste_urls (str): chemin du fichier json contenant la liste des URLs générées par un crawler
        champs (list, optional): champs sur lesquels appliquer les index. Valeur par défaut : ['title'].
        option (str, optional): option supplémentaire à appliquer au prétraitement (stemming ou None). Valeur par défaut : None.
        langage (str, optional): langue majoritaire des documents (essentiellement pour les stop words). Valeur par défaut : 'french'.
    """

    # Lire le fichier json contenant les URLs générés par un crawler 
    df = pd.read_json(liste_urls, encoding="utf-8")
    
    # Vérifier qu'il est possible de créer un index pour les champs indiqués
    if not all(e in list(df.columns) for e in champs) : 
        raise ValueError("Un ou plusieurs des champs entrés sont incorrects.")

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
    # Statistiques relatives aux champs 
    for col in champs : 
        # Nombre total de tokens pour le champs 'col'
        metadonnees[f"nombre_tokens_{col}"] = int(df[f'{col}_tokenize'].apply(lambda x: len(x)).sum())
        # Nombre total de tokens unique pour le champ 'col'
        metadonnees[f"nombre_tokens_unique_{col}"] = int(df[f'{col}_tokenize'].explode().nunique())
        # Moyenne des tokens par 'col' des documents 
        metadonnees[f"moyenne_tokens_{col}"] = int(round(df[f'{col}_tokenize'].apply(lambda x: len(x)).mean(),0)) 

    print(metadonnees)

    # Exporter les métadonnées dans un fichier json 
    nom_metadonnees = f"resultats/metadata.json" if option is None else f"resultats/{option}.metadata.json"
    export_json(nom_metadonnees, metadonnees, [', "', ',\n "'])
    
    # Construction des index (non positionnel et positionnel)

    # Création des index spécifiques à chaque champs 
    for col in champs : 

        index_non_pos = {} # Initialisation de l'index non positionnel
        index_pos = {}     # Initialisation de l'index positionnel

        # Parcourir chaque liste de tokens pour le champ 'col' et pour chaque document
        for id_doc, liste_tokens in enumerate(df[f'{col}_tokenize']):

            tokens_traites = set() # Pour ne pas traiter plusieurs fois le même token dans le cas de l'index positionnel

            # Parcourir chaque token de la liste de tokens 
            for token in liste_tokens :

                # Index non positionnel - Création de la liste inversée 
                index_non_pos.setdefault(token, [])
                if id_doc not in index_non_pos[token]: # Eviter les doublons 
                    index_non_pos[token].append(id_doc)

                # Index positionnel - Création de la liste inversée 
                index_pos.setdefault(token, {})
                index_pos[token].setdefault(str(id_doc), {'positions': [], 'count': 0})
                if token not in tokens_traites:

                    # Obtenir tous les indices où le token apparaît dans la liste des tokens
                    positions = [i for i, t in enumerate(liste_tokens) if t == token]
                    index_pos[token][str(id_doc)]['positions'].extend(positions)
                    index_pos[token][str(id_doc)]['count'] += len(positions)

                    # Ajouter le token à la liste des tokens déjà traités
                    tokens_traites.add(token)
        
        # Exporter les index vers des fichiers json
        nom_index = f"resultats/{col}.non_pos_index.json" if option is None else f"resultats/{option}.{col}.non_pos_index.json"
        export_json(nom_index, index_non_pos, ['], "', '],\n "'])
        nom_index = f"resultats/{col}.pos_index.json" if option is None else f"resultats/{option}.{col}.pos_index.json"
        export_json(nom_index, index_pos, ['}}, "', '}},\n "'])


if __name__=="__main__":
    # Liste des URLs générées par un crawler
    liste_urls = "donnees/crawled_urls.json"
    # Création d'un index avec un data processing simple
    index(liste_urls, champs=['title', 'content'])
    # Création d'un index avec un data processing avancé
    index(liste_urls, champs=['title', 'content'], option="stemming")