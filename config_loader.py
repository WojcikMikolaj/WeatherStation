from location_data import Location


config_path = './config'
config_locations = '/locations'
config_apikey = '/apikey'


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
