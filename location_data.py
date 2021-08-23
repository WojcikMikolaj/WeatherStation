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
