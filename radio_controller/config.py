import os


class Config:
    # General
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # gRPC
    GRPC_PORT = int(os.environ.get('GRPC_PORT', 50053))

    # SQLAlchemy DB URI (scheme + url)
    SQLALCHEMY_DB_URI = os.environ.get(
        'SQLALCHEMY_DB_URI', 'postgresql+psycopg2://postgres:postgres@db:5432/dp')
    SQLALCHEMY_DB_ENCODING = os.environ.get('SQLALCHEMY_DB_ENCODING', 'utf8')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_FUTURE = False


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    pass
