import asyncio
import threading

import tornado.ioloop
import tornado.web

from weather_data import WeatherData


class WeatherHandler(tornado.web.RequestHandler):
    def initialize(self, location_name, mutex: threading.Lock, data: WeatherData):
        self.location_name = location_name
        self.mutex = mutex
        self.data = data

    def get(self):
        self.write("Current weather for: " + self.location_name)
        self.mutex.acquire(True, -1)
        self.write(self.data.makeJSON().__str__())
        self.mutex.release()


def make_webapp(location_name, mutex: threading.Lock, data: WeatherData):
    return tornado.web.Application([
        (r"/weather", WeatherHandler,{'location_name': location_name, 'mutex': mutex, 'data': data}),
    ])


def start_webserver(location_name, mutex: threading.Lock, data: WeatherData):
    asyncio.set_event_loop(asyncio.new_event_loop())
    webapp = make_webapp(location_name, mutex, data)
    webapp.listen(4001)
    tornado.ioloop.IOLoop.current().start()
