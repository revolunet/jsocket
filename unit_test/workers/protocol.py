import threading

from settings import config
from protocols.commands import protocol_commands

class worker_protocol(threading.Thread):
    def __init__(self, queue):
        self.running = True
        self.queue = queue
        super(worker_protocol, self).__init__()
        self.setDaemon(True)

    def shutdown(self):
        self.running = False

    def run(self):
        while self.running is True or self.queue.empty() is False:
            item = self.queue.get()
            if item.get('engine', None) is not None and item['engine'].connect() is True:
                protocol_commands.test('connected', item['engine'])
                protocol_commands.test('auth', item['engine'])
                protocol_commands.test('create', item['engine'])
                protocol_commands.test('join', item['engine'])
                protocol_commands.test('chanMasterPwd', item['engine'])
                protocol_commands.test('chanAuth', item['engine'])
                protocol_commands.test('nick', item['engine'])
                protocol_commands.test('forward', item['engine'])
                protocol_commands.test('list', item['engine'])
                protocol_commands.test('message', item['engine'])
                protocol_commands.test('setStatus', item['engine'])
                protocol_commands.test('getStatus', item['engine'])
                protocol_commands.test('timeConnect', item['engine'])
                protocol_commands.test('history', item['engine'])
                protocol_commands.test('part', item['engine'])
                protocol_commands.test('remove', item['engine'])
                item['engine'].disconnect()
            self.queue.task_done()
