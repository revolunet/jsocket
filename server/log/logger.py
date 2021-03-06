##
# log.py
##

import os
import sys
import logging
import Queue
from time import gmtime, strftime
from commons.worker import WorkerLog
from config.settings import SETTINGS


class Log(object):
    """
    Logger, enregistre les actions effectue sur le server dans des fichiers de logs et print les message.
    """

    class __Log:
        def __init__(self):
            """
            Creation du fichier de log et initialisation du Queue worker
            """
            import os.path

            if os.path.exists(sys.path[0] + os.sep + 'log') != 1:
                os.mkdir(sys.path[0] + os.sep + 'log')
            self.__logFilename = sys.path[0] + os.sep + 'log/logs.log'
            logging.basicConfig(filename=self.__logFilename,
                                format="%(asctime)s - %(message)s")
            self.__logs = logging.getLogger("server")
            self.__logs.setLevel(logging.DEBUG)
            self.__logfile = open('%s%slog/logs_exception.log' %
                                  (sys.path[0], os.sep), 'a', 0)
            self.__logTraceback()
            self.__queue = Queue.Queue(SETTINGS.LOG_QUEUE_SIZE)
            for i in range(0, SETTINGS.LOG_THREADING_SIZE):
                WorkerLog(self.__queue).start()

        def add(self, msg, color='white'):
            """
            Ajoute un element dans la queue
            """
            self.__queue.put([msg, color])

        def get_color(self, color='white'):
            """
            Retourne la couleur shell correspondante au parametre
            """
            colors = {'white': '\033[1;37m$msg$\033[1;m',
                      'red': '\033[1;31m$msg$\033[1;m',
                      'yellow': '\033[1;33m$msg$\033[1;m',
                      'ired': '\033[1;48m$msg$\033[1;m',
                      'green': '\033[1;32m$msg$\033[1;m',
                      'blue': '\033[1;34m$msg$\033[1;m'}
            return colors.get(color)

        def dprint(self, msg, color='white'):
            """
            Affiche un message sur le sortie standard et le log dans un fichier
            """
            msgTime = '[%s]' % strftime('%A %d %B %Y %H:%M:%S, (UTC+0200)',
                                        gmtime())
            if SETTINGS.IS_DEBUG:
                if 'nt' not in os.name:
                    print "%s%s" % (msgTime, self.get_color(color).replace('$msg$', msg.strip(' \n')))
                else:
                    print msgTime + msg.strip(' \n')
            self.__logs.debug(msg)

        def __logTraceback(self):
            """
            Redirige la sortie d'erreurs vers un fichier
            """

            try:
                sys.stderr = self.__logfile
            except Exception:
                self.add("[!] Could not redirect errors: %s" % str(Exception), 'ired')

    instance = None

    def __new__(c):
        if not Log.instance:
            Log.instance = Log.__Log()
        return Log.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self.instance, attr, val)
