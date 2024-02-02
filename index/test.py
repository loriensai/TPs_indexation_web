import pandas as pd
import json
from nltk.tokenize import word_tokenize
from collections import defaultdict, Counter


# Exemple de DataFrame
data = {'title': ["C'est un exemple de un titre.",
                  "NLP avec Python est intéressant.",
                  "Traitement du langage de naturel."]}

df = pd.DataFrame(data)

# Tokenisation des titres
df['title_tokenize'] = df['title'].apply(lambda x: word_tokenize(x.lower()))

# Affichage du DataFrame avec la nouvelle colonne
print(df[['title', 'title_tokenize']])

index1 = {} # Initialisation de l'index 
index2 = {}

# Création d'une liste inversée pour chaque token 
for id_doc, liste_tokens in enumerate(df['title_tokenize']):

    processed_tokens = set() 
    for token in liste_tokens :

        # Index non positionnel
        index1.setdefault(token, [])
        if id_doc not in index1[token]:
            index1[token].append(id_doc)

        # Index positionnel
        index2.setdefault(token, {})
        index2[token].setdefault(str(id_doc), {'positions': [], 'count': 0})
        if token not in processed_tokens:

            # Obtenir tous les indices où le token apparaît dans la liste tokens
            positions = [i for i, t in enumerate(liste_tokens) if t == token]
            index2[token][str(id_doc)]['positions'].extend(positions)
            index2[token][str(id_doc)]['count'] += len(positions)

            # Ajouter le token à la liste des tokens déjà traités
            processed_tokens.add(token)

print(index1)
print('-----------------')
print(index2)

with open('test.json', 'w', encoding='utf-8') as fichier_json:
    json_str = json.dumps(index2, ensure_ascii=False, sort_keys=True)
    json_f = json_str.replace('}}, "', '}},\n "')
    fichier_json.write(json_f)


