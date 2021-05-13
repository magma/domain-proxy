import os


class Config:
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    API_PREFIX = os.environ.get('API_PREFIX', '/sas/v1')


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    TESTING = False
