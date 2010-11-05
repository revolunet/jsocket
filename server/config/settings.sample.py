"""
Settings sample
"""

import socket


class SETTINGS(object):
    """
    DEBUG CONFIGURATION
    """
    IS_DEBUG = True

    """
    SERVER CONFIGURATION
    """
    SERVER_PORT = 9999
    SERVER_HTTP_PORT = 81
    SERVER_WEBSOCKET_PORT = 8080
    SERVER_HOST = socket.gethostbyname(socket.gethostname())

    """
    CHANNEL/ROOM CONFIGURATION
    """
    CHANNEL_MAX_USERS = 100
    MASTER_PASSWORD = 'admin'
    CHANNEL_MASTER_PASSWORD = 'adminachan'

    """
    QUEUE CONFIGURATION
    """
    LOG_QUEUE_SIZE = 16
    WORKER_QUEUE_SIZE = 16

    """
    THREAD CONFIGURATION
    """
    LOG_THREADING_SIZE = 1
    WORKER_THREADING_SIZE = 1

    """
    WATCHDOG CONFIGURATION
    """
    WATCHDOG_SLEEP_TIME = 3
    WATCHDOG_MAX_IDLE_TIME = 1000
    WATCHDOG_HTTP_DISCONNECT_TIME = 10
    ROOM_EMPTY_TIME = 10

    """
    LOG CONFIGURATION
    """
    LOG_FILE_MAX_SIZE = 200000
    LOG_BACKUP_COUNT = 10

    """
    DEFAULT APPLICATION ON STARTUP
    """
    STARTUP_APP = [
        {'name': 'irc', 'app': 'default'},
        {'name': 'test', 'app': 'default'}
    ]
