import time
import datetime
import urllib.parse 
import urllib.request
from bs4 import BeautifulSoup
from protego import Protego
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import sessionmaker
from utils.url import URL
from dao.setup_bdd import setup_database
from dao.crawled_webpages_dao import afficher_table, mise_a_jour_age_table, trouver_webpage, inserer_webpage


def crawler(db_session, url_entree, max_liens=50, max_liens_page=5):
    """ Crawler 

    Args:
        db_session (Session): Une instance de session SQLAlchemy pour interagir avec la base de données
        url_entree (str): L'URL d'entrée unique (seed)
        max_liens (int, optional): Nombre maximum de liens à trouver et à télécharger. Valeur par défaut 50.
        max_liens_page (int, optional): Nombre maximum de liens à explorer par page. Valeur par défaut 5.
    """

    # Initialisation  
    frontier = [url_entree] # Frontier avec les URLs de la seed 
    urls_visitees = [] # URLs visitées pour ne pas les visiter plusieurs fois + critère d'arrêt
    sitemaps_visites = [] # URLs des sitemaps visités 
    urls_pb = [] # URLs où on n'est pas autorisés à crawler ou qui n'ont pas pu être téléchargées ou analysées
    
    # Vérifier la terminaison (si on doit continuer à crawler)
    while (len(urls_visitees) < max_liens) and len(frontier) : 

        # Prendre une URL de frontier
        url = URL(url=frontier.pop(0)) # Frontier FIFO : first in first out 

        print('Url en cours de traitement :', url)

        # Vérifier que le robot nous autorise à visiter la page
        try : 
            req = urllib.request.urlopen(url.get_url_robots) 
            if req.status == 200 :
                robots_txt = req.read().decode("utf-8") 
                rp = Protego.parse(robots_txt)
                autorisation = rp.can_fetch(url.text, "*")
                if autorisation : 
                    # Récupérer les sitemaps du site
                    for s in list(rp.sitemaps):
                        url_sitemap = URL(url=s)
                        if url_sitemap.text not in (frontier+sitemaps_visites) and url_sitemap.text != url.text:
                            frontier.append(url_sitemap.text)
        except: 
            autorisation = False

        # Politeness 
        time.sleep(5)

        # Autorisation de crawler
        if autorisation :

            # Télécharger la page
            try : 
                start_time = time.time()
                req = urllib.request.urlopen(url.text)
                end_time = time.time()
            except : 
                urls_pb.append(url.text)
                continue

            # Analyser le contenu 
            if req.status == 200 : 

                # Lecture du contenu de la page
                doc = req.read()

                # Fichier xml (les sitemaps)
                if url.type == "xml" : 

                    # Ajouter le sitemap aux sitemaps visités
                    sitemaps_visites.append(url.text)

                    # Analyser la page
                    soup = BeautifulSoup(doc,"xml")

                    # Récupérer les URLs
                    liens_recuperes = []
                    for lien in soup.find_all("url") :
                        lien_href = URL(url=lien.findNext("loc").text)
                        # S'assurer que max_liens_page sont ajoutés à frontier 
                        if len(liens_recuperes) < max_liens_page :
                            # S'assurer qu'ils n'ont pas été visités
                            if lien_href.text not in (urls_visitees + urls_pb + frontier + liens_recuperes):
                                liens_recuperes.append(lien_href.text)
                        else : 
                            break

                    # Ajouter les nouvelles URLs à frontier
                    frontier.extend(liens_recuperes)

                # Fichier html
                elif url.type == "html" :

                    # Ajouter l'URL analysée à urls_visitees
                    urls_visitees.append(url.text)

                    # Ajouter l'URL analysée en base de données
                    inserer_webpage(db_session, url.text)

                    # Analyser la page
                    soup = BeautifulSoup(doc, "html.parser")

                    # Récupérer les URLs
                    liens_recuperes = []
                    for lien in soup.find_all('a'):
                        lien_href = lien.get('href') 
                        if lien_href is not None and len(lien_href):
                            lien_href = URL(url=lien.get('href'))
                            # S'assurer que max_liens_page sont ajoutés à frontier 
                            if len(liens_recuperes) < max_liens_page :
                                # S'assurer qu'ils n'ont pas été visités
                                if lien_href.text not in (urls_visitees + urls_pb + frontier + liens_recuperes): 
                                    liens_recuperes.append(lien_href.text)
                            else : 
                                break
            
                    # Ajouter les nouvelles URLs à frontier
                    frontier.extend(liens_recuperes)
                
                # Mise à jour de l'âge des observations dans la base de données 
                mise_a_jour_age_table(db_session)
                
                # Politeness
                time.sleep(end_time - start_time)

        # Aucune autorisation pour crawler l'URL
        else : 
            urls_pb.append(url.text)
    
    # Ecrire les liens visités dans un fichier txt
    nom_fichier = "resultats/crawled_webpages.txt"
    with open(nom_fichier, 'w') as fichier:
        for ligne in urls_visitees:
            fichier.write(f"{ligne}\n")

    print(f"Les données ont été écrites dans {nom_fichier}. \n")

    # Affichage de la table finale en console 
    afficher_table(db_session)


if __name__=="__main__":
    # Etablir la connexion avec la base de données et créer la table 'webpages'
    db_session = setup_database() 
    # Paramètres
    url_entree = "https://ensai.fr/"
    max_liens = 50
    max_liens_page = 5
    # Lancement du crawler
    start_time = time.time()
    crawler(db_session, url_entree, max_liens, max_liens_page)
    end_time = time.time()
    print("Temps de compilation: ", end_time - start_time)