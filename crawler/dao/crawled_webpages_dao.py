from sqlalchemy.sql import text, func
# from setup_bdd import setup_database
import datetime

def afficher_table(session):

    # Requête
    select_query = text("SELECT * FROM webpages")

    # Exécution 
    res = session.execute(select_query)

    # Affichage
    for row in res : 
        print(row)

def mise_a_jour_age_table(session):

    # Requête
    update_query = text("UPDATE webpages SET age = CAST(EXTRACT(EPOCH FROM AGE(current_timestamp, derniere_visite)) / 60 AS INTEGER)")
    
    # Exécution
    session.execute(update_query)

    # Commit pour enregistrer les mises à jour dans la base de données
    session.commit()

def trouver_webpage(session, lien):

    # Requête
    select_query = text("SELECT * FROM webpages WHERE lien=:lien")
    data = {'lien': lien}

    # Exécution 
    res = session.execute(select_query, data)

    # Stockage des lignes trouvées
    resultat = [row for row in res]
    
    return True if len(resultat) else False

def inserer_webpage(session, lien):

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


# if __name__ == "__main__":
#     db_session = setup_database()
#     #inserer_webpage(db_session, 'http://example.com')
#     afficher_table(db_session)
#     mise_a_jour_age_table(db_session)