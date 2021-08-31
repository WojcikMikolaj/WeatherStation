#! /bin/python3
import ctypes
import datetime
import json
import socket
import string
import threading
from typing import Any

import requests
import argparse
import time
import logging
from sys import platform

import config_loader
import webserver
from connection_handler import listen_for_connections
from data_updater import update_data
from server_data import ServerData
from weather_data import WeatherData


if __name__ == '__main__':
    logging.basicConfig(filename='./logs/' + datetime.date.today().strftime('%d-%m-%y') + '.log',
                        filemode='a+', format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger('MainLogger')

    logger.info('Starting app')

    parser = argparse.ArgumentParser('Simple weather clock using OpenWeather\'s API')
    parser.add_argument('-l', '--location', type=type.__str__, default='',
                        help='Specifies user location, location name must be in config_locations file')
    args = parser.parse_args()

    location_name = args.location[1:-1]
    logger.info('Location name from cmd line: %s', location_name)

    location = config_loader.get_location(location_name)
    location.log(logger)

    apikey = config_loader.get_apikey()
    logger.debug('API key: %s', apikey)

    # send_request(location, apikey)

    mutex = threading.Lock()
    data = WeatherData()

    update_thread = threading.Thread(name='date_updater', target=update_data, args=(location, apikey, mutex, data,))
    update_thread.start()

    server_data = ServerData()
    sock = socket.socket(server_data.socket_type_first, server_data.socket_type_second)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server_data.address, server_data.port))

    listener_thread = threading.Thread(name='connection_listener', target=listen_for_connections,
                                       args=(sock, mutex, data,))
    listener_thread.start()

    webserver_thread = threading.Thread(name='web_thread', target=webserver.start_webserver, args=(location_name, mutex, data,))
    webserver_thread.start()

    while 1:
        pass
