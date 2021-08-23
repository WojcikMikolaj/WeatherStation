import json
import logging
import threading
import socket

from complex_encoder import ComplexEncoder
from weather_data import WeatherData


def listen_for_connections(sock: socket.socket, data_mutex: threading.Lock, data: WeatherData):
    logger = logging.getLogger('ConnectionsLogger')
    while 1:
        try:
            msg, address = sock.recvfrom(1024)
        except:
            continue
        logger.info('Received message: %s, from: %s', msg, address)
        data_mutex.acquire(True, -1)
        try:
            msg = str.encode(json.dumps(data, cls=ComplexEncoder))
            sock.sendto(msg, address)
            logger.info('Sent message: %s, to: %s', msg, address)
        except:
            pass
        data_mutex.release()
