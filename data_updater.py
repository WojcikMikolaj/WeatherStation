import json
import logging
import threading
import time
from sys import platform

import requests

from weather_data import WeatherData, Wind, Rain, Clouds


def update_data(location, apikey, mutex: threading.Lock, data: WeatherData):
    logger = logging.getLogger('UpdateLogger')
    while 1:
        response_text = send_request(location, apikey, logger)
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


def send_request(location, apikey, logger):
    post_url = 'https://api.openweathermap.org/data/2.5/weather?lat=' + str(location.latitude) + '&lon=' \
              + str(location.longitude) + '&appid=' + apikey
    if platform.startswith('linux'):
        post_url = post_url[0:-1]
    r = requests.post(post_url)
    logger.info('Post request:')
    logger.info('START')
    logger.info('URL')
    logger.info(post_url)
    logger.info('RESPONSE')
    logger.info(r.text)
    logger.info('END')
    return r.text
