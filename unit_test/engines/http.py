import urllib
import urllib2

class engine_http(object):
    refresh = '{"cmd": "refresh", "args": "null", "uid": "$uid", "channel": "protocol", "app": "protocol"}'

    def __init__(self, host, port):
        self.data = ''
        self.uid = None
        self.host = host
        self.port = port

    def connect(self):
        return True

    def send(self, json):
        if self.uid is not None:
            json = json.replace('$uid', self.uid)
        params = urllib.urlencode({'json': json})
        self.data = urllib2.urlopen('http://%s:%d/' % (self.host, self.port), params).read()
        return True

    def receive(self):
        if len(self.data) > 0:
            data = self.data
            self.data = ''
            return data
        if self.uid is not None:
            json = engine_http.refresh.replace('$uid', self.uid)
        params = urllib.urlencode({'json': json})
        data = urllib2.urlopen('http://%s:%d/' % (self.host, self.port), params).read()
        return data

    def disconnect(self):
        return True
