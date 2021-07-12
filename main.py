import ctypes
import datetime
import json
import string
import threading
import requests
import argparse
import time
import logging


config_path = './config'
config_locations = '/locations'
config_apikey = '/apikey'


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


class WeatherData:
    temperature = 0.0
    conditions = list()


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


def update_data(location, apikey, mutex:threading.Lock, data:WeatherData):
    while 1:
        response_text = send_request(location, apikey)
        json_data = json.loads(response_text)
        conditions = list()

        for weather in json_data['weather']:
            cond = weather['description']
            conditions.append(cond)
            logger.info(cond)
        temperature = float(json_data['main']['temp'])-273.0

        logger.info('temperature: ' + str(temperature)[0:5])
        logger.debug('copying data protected by mutex')

        mutex.acquire(True, -1)
        data.conditions = conditions.copy()
        data.temperature = temperature
        mutex.release()

        logger.debug('thread: ' + threading.current_thread().name + ' waiting 10 m for update')

        time.sleep(600)


def send_request(location, apikey):
    posturl = 'https://api.openweathermap.org/data/2.5/weather?lat=' + str(location.latitude) + '&lon=' \
              + str(location.longitude) + '&appid=' + apikey
    r = requests.post(posturl)
    logger.info('Post request:')
    logger.info('START')
    logger.info('URL')
    logger.info(posturl)
    logger.info('RESPONSE')
    logger.info(r.text)
    logger.info('END')
    return r.text


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

    #send_request(location, apikey)

    mutex = threading.Lock()
    data = WeatherData()

    update_thread = threading.Thread(name='date_updater', target=update_data, args=(location, apikey, mutex, data,))
    update_thread.start()

    while 1:
        pass
