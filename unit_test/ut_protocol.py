import sys
from Queue import Queue

from protocols.commands import protocol_commands
from engines.tcp import engine_tcp
from engines.http import engine_http
from stats.protocol import stat_protocol
from workers.protocol import worker_protocol
from settings import config

def main():
    stat_protocol.start(protocol_commands)
    queue = Queue(0)
    worker = worker_protocol(queue)
    worker.start()
    classname = 'engine_%s' % config.client_type
    engine = getattr(sys.modules['engines.%s' % config.client_type], classname)
    port = 'server_%s_port' % config.client_type
    for i in range(0, config.client_number):
        queue.put({'engine': engine(config.server_host, getattr(config, port))})
    worker.shutdown()
    worker.join()
    stat_protocol.show(config)

if __name__ == '__main__':
    main()
