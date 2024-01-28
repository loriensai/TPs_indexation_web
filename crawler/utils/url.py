import urllib.parse 


class URL:
    """ Création d'un objet URL pour obtenir des informations précises sur une URL """

    def __init__(self, url:str):
        self.text = url
        self.corriger_url() # Correction de l'URL au besoin 
        self.parsed_url = urllib.parse.urlparse(self.text)

    def corriger_url(self):
        """ Apporter une correction à l'URL pour ne pas explorer deux URLs identiques à un '/' près à la fin """
        if self.text[-1] != "/" : 
            self.text += "/"

    @property
    def type(self):
        """ Identifier le type de fichier associé à une URL

        Returns:
            str : "xml" ou "html" en fonction du type du fichier
        """
        return "xml" if "xml" in self.parsed_url.path else "html"

    @property
    def get_url_racine(self):
        """ Obtenir l'URL racine de l'URL

        Returns:
            str : URL racine (schéma + nom de domaine)
        """
        return f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"

    @property
    def get_url_robots(self):
        """ Obtenir l'URL menant au fichier robots.txt de la page web

        Ce dernier s'obtient en partant de l'URL racine et en ajoutant "/robots.txt"

        Returns:
            str : URL menant au fichier robots.txt 
        """
        return f"{self.get_url_racine}/robots.txt"
    
    def __str__(self):
        return self.text