import urllib.request
from bs4 import BeautifulSoup

def crawler(url_entree, max_liens=50):
    """ Crawler """
    print(url_entree)

if __name__=="__main__":
    url_entree = "https://ensai.fr/"
    crawler(url_entree)