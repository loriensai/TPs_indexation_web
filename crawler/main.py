import urllib.parse 
import urllib.request
import urllib.robotparser
import time
from bs4 import BeautifulSoup
from protego import Protego

def crawler(url_entree, max_liens=50, max_liens_page=5):
    """ Crawler """

    # Initialisation  
    frontier = [url_entree] # Frontier avec les URLs de la seed 
    urls_visitees = [] # URLs visitées pour ne pas les visiter plusieurs fois + critère d'arrêt
    urls_pb = []

    # Vérifier la terminaison (si on doit continuer à crawler)
    while (len(urls_visitees) < max_liens) and len(frontier) : 

        # Prendre une URL de frontier
        url = frontier.pop(0) # Frontier FIFO : first in first out 

        print('url', url)

        # Vérifier que le robot nous autorise à visiter la page
        parsed_url = urllib.parse.urlparse(url)
        url_robot = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        print(url_robot)
        try : 
            req = urllib.request.urlopen(url_robot) 
        except: 
            autorisation = False
        if req.status == 200 :
            robots_txt = req.read().decode("utf-8")
            rp = Protego.parse(robots_txt)
            autorisation = rp.can_fetch(url, "mybot")
            print(autorisation)
    
        if autorisation :
            
            # Télécharger la page
            try : 
                req = urllib.request.urlopen(url)
            except : 
                urls_pb.append(url)
                continue

            print(req.status)

            # Si le téléchargement a fonctionné
            if req.status == 200 :

                # Analyser la page
                html_doc = req.read()
                soup = BeautifulSoup(html_doc, "html.parser")

                # Récupérer les liens
                liens_recuperes = []
                for lien in soup.find_all('a'):
                    lien_href = lien.get('href')
                    # S'assurer que max_liens_page sont ajoutés à frontier 
                    if len(liens_recuperes) < max_liens_page :
                        # S'assurer qu'ils n'ont pas été visités
                        if (lien_href not in urls_visitees) and (lien_href not in urls_pb) and (lien_href not in frontier): 
                            liens_recuperes.append(lien_href)
        
                # Ajouter les nouvelles URLs à frontier
                frontier.extend(liens_recuperes)

                # Ajouter l'URL analysée à urls_visitees
                urls_visitees.append(url)

                print('frontier', frontier)
                print('pb', urls_pb)
                print('visited', urls_visitees)

            else : 
                urls_pb.append(url)
        
        else : 
            urls_pb.append(url)

        # Politeness 
        time.sleep(5)
    
    # Ecrire les liens visités dans un fichier txt
    nom_fichier = "crawler/crawled_webpages.txt"
    with open(nom_fichier, 'w') as fichier:
        for ligne in urls_visitees:
            fichier.write(f"{ligne}\n")

    print(f"Les données ont été écrites dans {nom_fichier}")


if __name__=="__main__":
    url_entree = "https://ensai.fr/"
    crawler(url_entree)