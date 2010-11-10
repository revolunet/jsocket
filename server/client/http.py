from twisted.web import resource
from log.logger import Log
from commons.approval import Approval
from commons.session import Session

import simplejson

class ClientHTTP(resource.Resource):
    """
    Classe HTTP utilisee par twisted
    """

    isLeaf = True
    pre_get = 'jsocket.api.onReceive(\''
    post_get = '\');'

    def getData(self, uid, get=False):
        """
        Recupere les reponses en suspend de l'utilisateur via son UID et
        les revoie separees par des \n
        """
        client = Session().get(uid)
        if client is None:
            return ''
        responses = client.getResponse()
        response = ''
        for res in responses:
            if '"connected"' not in res:
                if get is True:
                    response += "%s%s%s" % (ClientHTTP.pre_get,
                                            str(res), ClientHTTP.post_get)
                else:
                    response += "%s\n" % str(res)
        if len(response) > 0:
            Log().add('[http] Send: %s' % response)
        return response

    def render_GET(self, request):
        """
        Traite les informations envoye par GET.
        Necessite la cle json.
        """
        cuid = None
        if request.args.get('json', None) is not None:
            commands = request.args['json'][0].split("\n")
            for cmd in commands:
                jsoncmd = None
                try:
                    jsoncmd = simplejson.loads( cmd ).get('cmd')
                except:
                    pass
                
                if jsoncmd != 'refresh':
                    Log().add('[http-get] Receive: %s' % cmd)
                    
                if jsoncmd == 'httpCreateChannel':
                    return Approval().httpCreateChannel(cmd)
                elif jsoncmd == 'httpSendMessage':
                    return Approval().httpSendMessage(cmd)
                uid = Approval().validate(cmd, None, 'http')
                if uid is not None and cuid is None:
                    cuid = uid
                if '"connected"' in cmd:
                    return '%s{"from": "connected", "value": "%s"}%s%s' % (
                        ClientHTTP.pre_get, cuid, ClientHTTP.post_get,
                        'jsocket.core.http.connected();')
            return self.getData(cuid, True)
        return '%s{"from": "error", "value": "No JSON key"}%s' % (
            ClientHTTP.pre_get, ClientHTTP.post_get)

    def render_POST(self, request):
        """
        Traite les informations envoye par POST.
        Necessite la cle json.
        """
        cuid = None
        if request.args.get('json', None) is not None:
            Log().add('[http-post] Receive: %s' % request.args['json'][0])
            commands = request.args['json'][0].split("\n")
            for cmd in commands:
                if '"httpCreateChannel"' in cmd:
                    return Approval().httpCreateChannel(cmd)
                elif '"httpSendMessage"' in cmd:
                    return Approval().httpSendMessage(cmd)
                uid = Approval().validate(cmd, None, 'http')
                if uid is not None and cuid is None:
                    cuid = uid
                #if '"connected"' in cmd:
                    #return '{"from": "connected", "value": "%s"}' % cuid
            return self.getData(cuid)
        return '{"from": "error", "value": "No JSON key"}'
