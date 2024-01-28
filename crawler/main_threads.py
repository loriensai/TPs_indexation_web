import time
import datetime
import concurrent.futures
import urllib.parse 
import urllib.request
from bs4 import BeautifulSoup
from protego import Protego
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import sessionmaker
from utils.url import URL
from dao.setup_bdd import setup_database
from dao.crawled_webpages_dao import afficher_table, mise_a_jour_age_table, trouver_webpage, inserer_webpage
import threading
import queue


# Initialisation  
frontier = []
urls_visitees = [] # URLs visitées pour ne pas les visiter plusieurs fois + critère d'arrêt
sitemaps_visites = [] # URLs des sitemaps visités 
urls_pb = [] # URLs où on n'est pas autorisés à crawler ou qui n'ont pas pu être téléchargées ou analysées
urls_en_cours_de_traitement = [] # URLs en cours de traitement pour ne pas les ajouter à frontier quand un autre thread est en train de le traiter

# Ajout du verrou
frontier_lock = threading.Lock()


def crawler_worker(db_session, max_liens, max_liens_page):
    """ Fonction worker pour le crawler """

    global frontier, urls_visitees, sitemaps_visites, urls_pb, urls_en_cours_de_traitement

    while (len(urls_visitees) < max_liens) and len(frontier):

        # Prendre une URL de frontier
        with frontier_lock:
            if not frontier:
                break
            url = URL(url=frontier.pop(0))  # Frontier FIFO : first in first out 
            urls_en_cours_de_traitement.append(url.text)

        print(f'URL en cours de traitement par {threading.current_thread().name}: {url}')

        # Vérifier que le robot nous autorise à visiter la page
        try: 
            req = urllib.request.urlopen(url.get_url_robots) 
            if req.status == 200:
                robots_txt = req.read().decode("utf-8") 
                rp = Protego.parse(robots_txt)
                autorisation = rp.can_fetch(url.text, "*")
                if autorisation: 
                    # Récupérer les sitemaps du site
                    with frontier_lock : 
                        for s in list(rp.sitemaps):
                            url_sitemap = URL(url=s)
                            if url_sitemap.text not in (frontier + sitemaps_visites + urls_en_cours_de_traitement) and url_sitemap.text != url.text:
                                frontier.append(url_sitemap.text)
        except: 
            autorisation = False

        # Politeness 
        time.sleep(5)

        # Autorisation de crawler
        if autorisation:

            # Télécharger la page
            try: 
                start_time = time.time()
                req = urllib.request.urlopen(url.text)
                end_time = time.time()
            except: 
                urls_pb.append(url.text)
                continue

            # Analyser le contenu 
            if req.status == 200: 

                # Lecture du contenu de la page
                doc = req.read()

                # Fichier xml (les sitemaps)
                if url.type == "xml": 

                    # Ajouter le sitemap aux sitemaps visités
                    sitemaps_visites.append(url.text)

                    # Analyser la page
                    soup = BeautifulSoup(doc,"xml")

                    # Récupérer les URLs
                    liens_recuperes = []
                    for lien in soup.find_all("url"):
                        lien_href = URL(url=lien.findNext("loc").text)
                        with frontier_lock : 
                            # S'assurer que max_liens_page sont ajoutés à frontier 
                            if len(liens_recuperes) < max_liens_page:
                                # S'assurer qu'ils n'ont pas été visités
                                if lien_href.text not in (urls_visitees + urls_pb + frontier + liens_recuperes + urls_en_cours_de_traitement):
                                    liens_recuperes.append(lien_href.text)
                            else: 
                                break

                    # Ajouter les nouvelles URLs à frontier
                    with frontier_lock:
                        frontier.extend(liens_recuperes)

                # Fichier html
                elif url.type == "html":
                    
                    # Ajouter l'URL analysée à urls_visitees et en base de données
                    with frontier_lock : 
                        urls_visitees.append(url.text)
                        inserer_webpage(db_session, url.text)

                    # Analyser la page
                    soup = BeautifulSoup(doc, "html.parser")

                    # Récupérer les URLs
                    liens_recuperes = []
                    for lien in soup.find_all('a'):
                        lien_href = lien.get('href') 
                        if lien_href is not None and len(lien_href):
                            lien_href = URL(url=lien.get('href'))
                            with frontier_lock : 
                                # S'assurer que max_liens_page sont ajoutés à frontier
                                if len(liens_recuperes) < max_liens_page:
                                    # S'assurer qu'ils n'ont pas été visités
                                    if lien_href.text not in (urls_visitees + urls_pb + frontier + liens_recuperes + urls_en_cours_de_traitement): 
                                        liens_recuperes.append(lien_href.text)
                                else: 
                                    break
            
                    # Ajouter les nouvelles URLs à frontier
                    with frontier_lock:
                        frontier.extend(liens_recuperes)
                
                # Mise à jour de l'âge dans la base de données
                with frontier_lock: 
                    mise_a_jour_age_table(db_session)
                
                # Politeness
                time.sleep(end_time - start_time)

        # Aucune autorisation pour crawler l'URL
        else: 
            urls_pb.append(url.text)

        # Suppression de l'URLs qui était en cours de traitement 
        urls_en_cours_de_traitement.remove(url.text)

def crawler(db_session, url_entree, max_liens=50, max_liens_page=5, num_threads=3):
    """ Crawler """

    global frontier, urls_visitees, sitemaps_visites, urls_pb

    # Initialisation 
    url = URL(url=url_entree)
    req = urllib.request.urlopen(url.get_url_robots) 
    if req.status == 200:
        robots_txt = req.read().decode("utf-8") 
        rp = Protego.parse(robots_txt)
        autorisation = rp.can_fetch(url.text, "*")
        if autorisation: 
            # Récupérer les sitemaps du site
            for s in list(rp.sitemaps):
                url_sitemap = URL(url=s)
                with frontier_lock:
                    if url_sitemap.text not in (frontier + sitemaps_visites) and url_sitemap.text != url.text:
                        frontier.append(url_sitemap.text)
    urls_visitees.append(url.text)
    print('frontier',frontier)
    print(urls_visitees)

    # Créer la liste des threads
    threads = []

    # Lancer les threads
    for _ in range(num_threads):
        thread = threading.Thread(target=crawler_worker, args=(db_session, max_liens, max_liens_page))
        thread.start()
        threads.append(thread)

    # Attendre que tous les threads se terminent
    for thread in threads:
        thread.join()

    # Ecrire les liens visités dans un fichier txt
    nom_fichier = "resultats/crawled_webpages_threads.txt"
    with open(nom_fichier, 'w') as fichier:
        for ligne in urls_visitees:
            fichier.write(f"{ligne}\n")

    print(f"Les données ont été écrites dans {nom_fichier}. \n")

    # Mise à jour de l'âge dans la base de données 
    mise_a_jour_age_table(db_session)

    # Affichage de la table finale en console 
    afficher_table(db_session)


if __name__=="__main__":
    db_session = setup_database()
    url_entree = "https://ensai.fr/"
    max_liens = 50
    max_liens_page = 5
    num_threads = 3
    start_time = time.time()
    crawler(db_session, url_entree, max_liens, max_liens_page, num_threads)
    end_time = time.time()
    print("Temps de compilation: ", end_time - start_time)