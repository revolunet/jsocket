import time
import urllib


class History(object):
    """
    Garde en memoire les messages d'un channel
    """

    def __init__(self):
        self.__history = []

    def add(self, uid, json):
        """
        Ajout un message a l'historique du channel
        """
        self.__history.append({
            'time': time.time(),
            'uid': uid,
            'json': urllib.quote(str(json))
        })

    def get(self):
        """
        Renvoie la liste des messages du channel
        """
        return self.__history

    def get_from(self, start, end):
        """
        Renvoie la liste des messages du channel compris entre start et end ( microtime )
        """
        history = []
        for h in self.__history:
            if h.time <= start and h.time >= end:
                history.append(h)
        return history

    def flush(self):
        """
        Reset la taille de l'historique
        """
        self.__history = []
