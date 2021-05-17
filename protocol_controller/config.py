import os


class Config:
    # General
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    API_PREFIX = os.environ.get('API_PREFIX', '/sas/v1')

    # gRPC
    GRPC_SERVICE = os.environ.get('GRPC_SERVICE', 'domain-proxy-radio-controller')
    GRPC_PORT = int(os.environ.get('GRPC_PORT', 50053))


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    TESTING = False
