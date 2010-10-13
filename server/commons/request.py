import urllib

from log.logger import Log
class Request(object):
    def __init__(self, vhost, uid, status):
        self.vhost = vhost
        self.uid = uid
        self.status = status

    def send(self):
        if self.vhost and self.uid and self.status:
            Log().add("[+] Channel : send status %s for %s to %s" % (self.status, self.uid, self.vhost), 'blue')
            try:
                urllib.urlopen("%s/jsocket?uid=%s&status=%s" % (self.vhost, self.uid, self.status))
            except IOError, e:
                if hasattr(e, 'reason'):
                    Log().add("[!] cannot send http status : %s" % e.reason, 'red')
                elif hasattr(e, 'code'):
                    Log().add("[!] cannot send http status : %s" % e.code, 'red')
                else:
                    Log().add("[!] cannot send http status", 'red')
                