import urllib.parse 
import urllib.request
import time
from bs4 import BeautifulSoup
from protego import Protego
from url import URL

def crawler(url_entree, max_liens=50, max_liens_page=5):
    """ Crawler """

    # Initialisation  
    frontier = [url_entree] # Frontier avec les URLs de la seed 
    urls_visitees = [] # URLs visitées pour ne pas les visiter plusieurs fois + critère d'arrêt
    sitemaps_visites = [] 
    urls_pb = [] # URLs où on n'est pas autorisés à crawler ou qui n'ont pas pu être téléchargées ou analysées
    
    # Vérifier la terminaison (si on doit continuer à crawler)
    while (len(urls_visitees) < max_liens) and len(frontier) : 

        # Prendre une URL de frontier
        url = URL(url=frontier.pop(0)) # Frontier FIFO : first in first out 

        print('url', url)

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
                        if s not in (frontier+sitemaps_visites) and s != url.text:
                            frontier.append(s)
        except: 
            autorisation = False
        
        print(url.get_url_robots, autorisation)

        # Politeness 
        time.sleep(5)
    
        # L'URL est un sitemap de type XML
        if autorisation and url.type == "xml":

            # Télécharger la page
            try : 
                req = urllib.request.urlopen(url.text)
            except : 
                urls_pb.append(url.text)
                continue

            # Ajouter le sitemap aux sitemaps visités
            sitemaps_visites.append(url.text)

            # Analyser le contenu du sitemap
            if req.status == 200 : 
                soup = BeautifulSoup(req.read(),"xml")
                # URLS
                liens_recuperes = []
                for urls in soup.find_all("url") :
                    print('url',urls.findNext("loc").text)
                    lien_href = URL(url=urls.findNext("loc").text)
                    # S'assurer que max_liens_page sont ajoutés à frontier 
                    if len(liens_recuperes) < max_liens_page :
                        # S'assurer qu'ils n'ont pas été visités
                        if lien_href.text not in (urls_visitees + urls_pb + frontier + liens_recuperes):
                            liens_recuperes.append(lien_href.text)
                    else : 
                        break
                # Ajouter les nouvelles URLs à frontier
                frontier.extend(liens_recuperes)
            else : 
                urls_pb.append(url.text)

        # L'URL est une page HTML 
        elif autorisation and url.type == "html":
            
            # Télécharger la page
            try : 
                req = urllib.request.urlopen(url.text)
            except : 
                urls_pb.append(url.text)
                continue

            # Si le téléchargement a fonctionné
            if req.status == 200 :

                # Analyser la page
                html_doc = req.read()
                soup = BeautifulSoup(html_doc, "html.parser")

                # Ajouter l'URL analysée à urls_visitees
                urls_visitees.append(url.text)

                # Récupérer les liens
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

            else : 
                urls_pb.append(url.text)
        
        # Aucune autorisation pour crawler l'URL
        else : 
            urls_pb.append(url.text)
        
        print('frontier', frontier)
        print('pb', urls_pb)
        print('visited', urls_visitees)
        print('sitemaps visités', sitemaps_visites)

        # Politeness 
        time.sleep(5)
    
    # Ecrire les liens visités dans un fichier txt
    nom_fichier = "crawler/resultats/crawled_webpages.txt"
    with open(nom_fichier, 'w') as fichier:
        for ligne in urls_visitees:
            fichier.write(f"{ligne}\n")

    print(f"Les données ont été écrites dans {nom_fichier}")


if __name__=="__main__":
    url_entree = "https://ensai.fr/"
    crawler(url_entree)