from sqlalchemy.sql import text, func
import datetime


def afficher_table(session):
    """ Affichage de la table 'webpages' en console 

    Args:
        session (Session): Une instance de session SQLAlchemy pour interagir avec la base de données
    """
    # Requête
    select_query = text("SELECT * FROM webpages")

    # Exécution 
    res = session.execute(select_query)

    # Affichage
    for row in res : 
        print(row)

def mise_a_jour_age_table(session):
    """ Mise à jour de l'âge des pages web dans la table 'webpages'

    L'âge d'une page vaut 0 lorsque la page est indexée pour la première fois.
    Puis il augmente jusqu'à ce que la page soit à nouveau explorée.
    Lorsque la page est à nouveau explorée, son âge vaut à nouveau 0. 

    Ici, l'âge est exprimé en minutes et se calcule en faisant la différence entre la date à laquelle la fonction est appelée et la date de la dernière exploration

    Args:
        session (Session): Une instance de session SQLAlchemy pour interagir avec la base de données
    """
    # Requête
    update_query = text("UPDATE webpages SET age = CAST(EXTRACT(EPOCH FROM AGE(current_timestamp, derniere_visite)) / 60 AS INTEGER)")
    
    # Exécution
    session.execute(update_query)

    # Commit pour enregistrer les mises à jour dans la base de données
    session.commit()

def trouver_webpage(session, lien):
    """ Véifier si une page web est déjà présente dans la base de données 

    Args:
        session (Session): Une instance de session SQLAlchemy pour interagir avec la base de données
        lien (str): L'URL de la page web

    Returns:
        bool : True si la page web existe dans la base de données et False sinon
    """
    # Requête
    select_query = text("SELECT * FROM webpages WHERE lien=:lien")
    data = {'lien': lien}

    # Exécution 
    res = session.execute(select_query, data)

    # Stockage des lignes trouvées
    resultat = [row for row in res]
    
    return True if len(resultat) else False

def inserer_webpage(session, lien):
    """ Insertion ou modification d'une page web dans la base de données 

    Si la page web n'existe pas en base de données, alors elle est ajoutée.
    Si la page web existe, ses informations sont mises à jour.

    Args:
        session (Session): Une instance de session SQLAlchemy pour interagir avec la base de données
        lien (str): L'URL de la page web
    """
    # Traitement d'une nouvelle page jamais rencontrée
    if not(trouver_webpage(session, lien)) : 

        # Requête
        insert_query = text("INSERT INTO webpages (lien, age) VALUES (:lien, :age)")
        data = {'lien': lien, 'age': 0}

        # Exécutez la requête d'insertion
        session.execute(insert_query, data)

        # Commit pour effectuer l'insertion dans la base de données
        session.commit()
    
    # Traitement d'une page déjà rencontrée
    else : 
        
        # Requête
        update_query = text("UPDATE webpages SET age = :nouveau_age, derniere_visite = :nouveau_derniere_visite WHERE lien = :lien_a_mettre_a_jour")
        data = {'lien_a_mettre_a_jour': lien, 'nouveau_age': 0, 'nouveau_derniere_visite': datetime.datetime.utcnow()}
        
        # Exécution
        session.execute(update_query, data)

        # Commit pour enregistrer les mises à jour dans la base de données
        session.commit()