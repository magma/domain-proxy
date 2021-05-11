import os


class Config:
    # General
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

    # gRPC
    GRPC_PORT = int(os.environ.get('GRPC_PORT', 50053))


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    pass
