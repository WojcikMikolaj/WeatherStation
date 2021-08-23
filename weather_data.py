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
