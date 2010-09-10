import time

class stat_protocol(object):
    errorTotal = 0
    errors = { }
    errorsDetails = { }
    begin = 0
    protocol = None

    @staticmethod
    def start(protocol):
        stat_protocol.protocol = protocol
        stat_protocol.begin = time.time()

    @staticmethod
    def add(command, detail):
        if stat_protocol.errors.get(command, None) is None:
            stat_protocol.errors[command] = 0
            stat_protocol.errorsDetails[command] = [ ]
        stat_protocol.errors[command] += 1
        stat_protocol.errorTotal += 1
        stat_protocol.errorsDetails[command].append("\n%s" % detail)

    @staticmethod
    def show_header(config):
        print '-----------------------------------------------------------------------'
        print 'Server:'
        print '-----------------------------------------------------------------------'
        print ' - Host: %s' % str(config.server_host)
        print ' - TCP port: %d' % config.server_tcp_port
        print ' - HTTP port: %d' % config.server_http_port
        print ' - WebSocket port: %d' % config.server_websocket_port
        print '-----------------------------------------------------------------------'
        print 'Results:'
        print '-----------------------------------------------------------------------'

    @staticmethod
    def show_results(config):
        totalTime = float(time.time() - stat_protocol.begin)
        totalCommand = len(stat_protocol.protocol.commands) * config.client_number
        print ' - Client protocol used: %s' % config.client_type
        print ' - Total executed commands: %d' % totalCommand
        print '  . Commands per client: %d' % len(stat_protocol.protocol.commands)
        print ' - Total time (secs): %s' % str(totalTime)
        print '  . Average secs per command: %s' % str(totalTime / totalCommand)
        print '  . Average secs per client: %s' % str(totalTime / config.client_number)
        print '  . Average commands per secs: %s' % str(float(totalCommand) / float(totalTime))
        print ' - For %d Clients it founds %d errors:' % (config.client_number, stat_protocol.errorTotal)
        print '  . Average error %% per command: %s' % str(float(stat_protocol.errorTotal) / float(totalCommand))
        print '-----------------------------------------------------------------------'


    @staticmethod
    def show_errors(config):
        if stat_protocol.errorTotal == 0:
            print ' - \\o/ No error found. You just made a great JusDeChaussette TODAY !'
            print '-----------------------------------------------------------------------'
            return True
        print 'Errors:'
        for (command, nbError) in stat_protocol.errors.items():
            print '-----------------------------------------------------------------------'
            print '[%s] Found %d errors' % (command, nbError)
            if config.debug == True:
                print '[%s] Details:' % command
                for detail in stat_protocol.errorsDetails[command]:
                    print detail
        print '-----------------------------------------------------------------------'
        return False

    @staticmethod
    def show(config):
        stat_protocol.show_header(config)
        stat_protocol.show_results(config)
        stat_protocol.show_errors(config)

    @staticmethod
    def add(command, detail):
        if stat_protocol.errors.get(command, None) is None:
            stat_protocol.errors[command] = 0
            stat_protocol.errorsDetails[command] = [ ]
        stat_protocol.errors[command] += 1
        stat_protocol.errorTotal += 1
        stat_protocol.errorsDetails[command].append("\n%s" % detail)
