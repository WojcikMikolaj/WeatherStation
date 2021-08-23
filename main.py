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

config_path = './config'
config_locations = '/locations'
config_apikey = '/apikey'


class ComplexEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, 'makeJSON'):
            return o.makeJSON()
        else:
            return json.JSONEncoder.default(self, o)


class Location:
    name = ''
    latitude = 0.0
    longitude = 0.0

    def print(self):
        print('Name: %s\n', self.name)
        print('latitude: %f\n', self.latitude)
        print('longitude: %f\n', self.longitude)

    def log(self, logger):
        logger.info('Location data')
        logger.info('   name: %s', self.name)
        logger.info('   latitude: %f', self.latitude)
        logger.info('   longitude: %f', self.longitude)


class Jsonable:
    def makeJSON(self):
        return self.__dict__


class Wind(Jsonable):
    speed = 0.0
    deg = 0


class Rain(Jsonable):
    last_hour_forecast = 0.0


class Clouds(Jsonable):
    cloudiness = 0


class WeatherData(Jsonable):
    temperature = 0.0
    feels_like = 0.0
    pressure = 0
    humidity = 0
    visibility = 0
    wind = Wind()
    rain = Rain()
    clouds = Clouds()
    conditions = list()


class ServerData:
    port = 4000
    address = '127.0.0.1'
    socket_type_first = socket.AF_INET
    socket_type_second = socket.SOCK_DGRAM


def get_location(location_name):
    file = open(config_path + config_locations, 'r')
    location = Location()
    condition = 1
    while condition:
        try:
            text = file.readline()
            if '' == text:
                condition = 0
            text = text[0:-1]
            if location_name == text:
                location.name = text
                location.latitude = float(file.readline())
                location.longitude = float(file.readline())
                condition = 0
        except:
            condition = 0
    return location


def get_apikey():
    file = open(config_path + config_apikey, 'r')
    apikey = ''
    try:
        apikey = file.readline()
    finally:
        return apikey


def update_data(location, apikey, mutex: threading.Lock, data: WeatherData):
    while 1:
        response_text = send_request(location, apikey)
        json_data = json.loads(response_text)
        conditions = list()

        for weather in json_data['weather']:
            cond = weather['description']
            conditions.append(cond)
            logger.info(cond)
        temperature = float(json_data['main']['temp'])-273.0
        feels_like = float(json_data['main']['feels_like'])-273.0
        pressure = int(json_data['main']['pressure'])
        humidity = int(json_data['main']['humidity'])
        visibility = int(json_data['visibility'])

        wind = Wind()
        if 'wind' in json_data:
            wind.deg = int(json_data['wind']['deg'])
            wind.speed = float(json_data['wind']['speed'])

        rain = Rain()
        if 'rain' in json_data:
            rain.last_hour_forecast = float(json_data['rain']['1h'])

        clouds = Clouds()
        if 'clouds' in json_data:
            clouds.cloudiness = int(json_data['clouds']['all'])

        logger.info('temperature: ' + str(temperature)[0:5])
        logger.debug('copying data protected by mutex')

        mutex.acquire(True, -1)
        data.conditions = conditions.copy()
        data.temperature = temperature
        data.rain = rain
        data.clouds = clouds
        data.humidity = humidity
        data.wind = wind
        data.pressure = pressure
        data.visibility = visibility
        data.feels_like = feels_like
        mutex.release()

        logger.debug('thread: ' + threading.current_thread().name + ' waiting 10 m for update')

        time.sleep(600)


def send_request(location, apikey):
    posturl = 'https://api.openweathermap.org/data/2.5/weather?lat=' + str(location.latitude) + '&lon=' \
              + str(location.longitude) + '&appid=' + apikey
    if platform.startswith('linux'):
        posturl = posturl[0:-1]
    r = requests.post(posturl)
    logger.info('Post request:')
    logger.info('START')
    logger.info('URL')
    logger.info(posturl)
    logger.info('RESPONSE')
    logger.info(r.text)
    logger.info('END')
    return r.text


def listen_for_connections(sock: socket.socket, data_mutex: threading.Lock, data: WeatherData):
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

    location = get_location(location_name)
    location.log(logger)

    apikey = get_apikey()
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

    while 1:
        pass
