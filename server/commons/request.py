import urllib


class Request(object):
    def __init__(self, vhost, uid, status):
        self.vhost = vhost
        self.uid = uid
        self.status = status

    def send(self):
        if self.vhost and self.uid and self.status:
            urllib.urlopen("%s/jsocket?uid=%s&status=%s" % (self.vhost, self.uid, self.status))