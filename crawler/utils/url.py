import urllib.parse 


class URL:
    """ Création d'un objet URL pour obtenir des informations précises sur une URL """

    def __init__(self, url:str):
        self.text = url
        self.corriger_url()
        self.parsed_url = urllib.parse.urlparse(self.text)

    def corriger_url(self):
        if self.text[-1] != "/" : 
            self.text += "/"

    @property
    def type(self):
        return "xml" if "xml" in self.parsed_url.path else "html" 

    @property
    def get_url_racine(self):
        return f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"

    @property
    def get_url_robots(self):
        return f"{self.get_url_racine}/robots.txt"
    
    def __str__(self):
        return self.text
    
# Exemple d'utilisation
# url_obj = URL("https://example.com")
# print(url_obj)  # Affiche directement url_obj.text
# print(str(url_obj))  # Affiche également url_obj.text
# print(url_obj.get_url_racine)
# print(url_obj.get_url_robots)
# print(url_obj.type)