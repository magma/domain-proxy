import os


class Config:
    # General
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    REQUEST_PROCESSING_INTERVAL = int(
        os.environ.get('REQUEST_PROCESSING_INTERVAL', 10))
    REQUEST_MAPPING_FILE_PATH = os.environ.get(
        'REQUEST_MAPPING_FILE_PATH', 'mappings/request_mapping.yml')

    # Services
    SAS_URL = os.environ.get('SAS_URL', 'https://fake-sas-service/v1.2')
    RC_INGEST_URL = os.environ.get('RC_INGEST_URL', '')

    # SQLAlchemy DB URI (scheme + url)
    SQLALCHEMY_DB_URI = os.environ.get('SQLALCHEMY_DB_URI', 'postgresql+psycopg2://postgres:postgres@db:5432/dp')
    SQLALCHEMY_DB_ENCODING = os.environ.get('SQLALCHEMY_DB_ENCODING', 'utf8')
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_FUTURE = False

    # Security
    CC_CERT_PATH = os.environ.get(
        'CC_CERT_PATH', '/backend/configuration_controller/certs/device_c.cert')
    CC_SSL_KEY_PATH = os.environ.get(
        'CC_SSL_KEY_PATH', '/backend/configuration_controller/certs/device_c.key')
    SAS_CERT_PATH = os.environ.get(
        'SAS_CERT_PATH', '/backend/configuration_controller/certs/ca.cert')


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    SQLALCHEMY_ECHO = False
    pass
