import time
import random
from twisted.internet import reactor
from config.settings import SETTINGS


class Client(object):
    """
    Interface commune aux clients TCP et HTTP.
    Regroupe les informations qui caracterise un client.
    """

    def __init__(self, room):
        """
        HTTP/TCP Client constructeur.
        """
        self.room = room
        self.master = False
        self.nickName = None
        self.master_password = SETTINGS.MASTER_PASSWORD
        self.unique_key = str(hex(random.getrandbits(64)))
        self.status = 'online'
        self.connection_time = int(time.time())
        self.last_action = self.connection_time
        self.room_name = None
        self.callback = None
        self.response = []
        self.type = None
        self.vhost = None

    def getName(self):
        """
        Return : Si l utilisateur n a pas de nickname
        on retourne la unique_key sinon son nickname -> string
        """
        if self.nickName == None:
            return self.unique_key
        return self.nickName

    def addResponse(self, command):
        """
        Ajoute une commande reponse a la Queue en cours
        """
        from log.logger import Log

        self.last_action = time.time()
        if self.callback is not None:
            if callable(self.callback):
                Log().add('[%s] Send: %s' % (str(self.type),
                                             str(command)), 'green')
                reactor.callFromThread(self.callback, [command])
            else:
                self.callback = None
            command = None
        if command is not None:
            self.response.append(command)

    def updateLastAction(self):
        """
        Mets a jour la derniere action utilisateur
        """

        self.last_action = time.time()

    def getResponse(self):
        """
        Retourne les commandes en attente d'envoie
        """
        from log.logger import Log

        self.last_action = time.time()
        res = self.response
        self.response = []
        if len(res) > 0:
            Log().add('[%s] Send: %s' % (str(self.type), str(res)), 'green')
        return res
