import urllib
import threading
from log.logger import Log

class Request(threading.Thread):
    def __init__(self, vhost, uid, status):
        self.vhost = vhost
        self.uid = uid
        self.status = status
        threading.Thread.__init__(self)

    def run(self):
        if self.vhost and self.uid and self.status:
            import socket
            socket.setdefaulttimeout(5)

            Log().add("[+] Channel : send status %s for %s to %s" % (self.status, self.uid, self.vhost), 'blue')
            try:
                urllib.urlopen("%s/jsocket?uid=%s&status=%s" % (self.vhost, self.uid, self.status))
            except IOError, e:
                if hasattr(e, 'reason'):
                    Log().add("[!] cannot send http status : %s" % e.reason, 'red')
                elif hasattr(e, 'code'):
                    Log().add("[!] cannot send http status : %s" % e.code, 'red')
                elif hasattr(e, 'strerror'):
                    Log().add("[!] cannot send http status : %s" % e.strerror, 'red')
                else:
                    Log().add("[!] cannot send http status", 'red')
