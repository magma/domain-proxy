import os

import db_service.config


class Config:
    # General
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # gRPC
    GRPC_PORT = int(os.environ.get('GRPC_PORT', 50053))

    # SQLAlchemy DB URI (scheme + url)
    SQLALCHEMY_DB_URI = db_service.config.Config().SQLALCHEMY_DB_URI
    SQLALCHEMY_DB_ENCODING = db_service.config.Config().SQLALCHEMY_DB_ENCODING
    SQLALCHEMY_ECHO = db_service.config.Config().SQLALCHEMY_ECHO
    SQLALCHEMY_FUTURE = db_service.config.Config().SQLALCHEMY_FUTURE


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    pass
