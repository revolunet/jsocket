from server.websocket import WebSocketHandler
from commons.approval import Approval
from commons.session import Session
from log.logger import Log


class ClientWebSocket(WebSocketHandler):
    """
    Classe WebSocket HTML5 utilisee par twisted
    """
    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)
        self.uid = None
        self.connected = False

    def callbackSend(self, responses):
        """
        Callback appele par le :func:`WorkerParser`
        lorsque des reponses sont pretes
        """
        if responses is None:
            return False
        for json in responses:
            if json is not None and len(json) and \
                   '"connected"' not in json:
                self.send(json)
        return True

    def frameReceived(self, frame):
        """
        Methode appelee lorsque l'utilisateur recoit des donnees
        """
        Log().add('[websocket] Received: %s' % frame)
        self.connected = True
        commands = frame.split("\n")
        uid = None
        for cmd in commands:
            if len(cmd) > 0:
                uid = Approval().validate(cmd, self.callbackSend, 'websocket')
            if '"connected"' in cmd:
                self.send('{"from": "connected", "value": "%s"}' % uid)
            if uid is not None:
                self.uid = uid

    def connectionLost(self, reason):
        """
        Methode appelee lorsqu'un utilisateur se deconnecte
        """
        self.connected = False
        if self.uid is not None:
            Log().add('[websocket] Logout %s' % str(self.uid))
            Session().delete(self.uid)
        self.transport.loseConnection()

    def send(self, msg):
        """
        Methode permettant d'ecrire le message sur
        la socket si l'utilisateur est connecte
        """
        if self.connected is True:
            msg = msg.encode('utf8')
            self.transport.write(msg)

    @property
    def socket(self):
        return self.transport.getHandle()
