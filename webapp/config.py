
class Config(object):
  DATABASE = '/tmp/flaskr.db'
  DEBUG = True
  SECRET_KEY = 'dev key'
  USERNAME = 'admin'
  PASSWORD = 'default'
  TESTING = False

class ProductionConfig(Config):
  DATABASE_URI = '/tmp/flaskr.db'
  DEBUG = False

class DevelopmentConfig(Config):
  DEBUG = True

class TestingConfig(Config):
  TESTING = True