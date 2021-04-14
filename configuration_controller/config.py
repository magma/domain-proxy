import os
from urllib.parse import quote


class Config:
    # General
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    REQUEST_PROCESSING_INTERVAL = int(os.environ.get('REQUEST_PROCESSING_INTERVAL', 10))
    REQUEST_MAPPING_FILE_PATH = os.environ.get('REQUEST_MAPPING_FILE_PATH', 'mappings/request_mapping.yml')

    # Services
    SAS_URL = os.environ.get('SAS_URL', 'https://fake-sas-service/v1.2')
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
    RC_INGEST_URL = os.environ.get('RC_INGEST_URL', '')

    # Security
    CC_CERT_PATH = os.environ.get('CC_CERT_PATH', '/backend/configuration_controller/certs/device_c.cert')
    CC_SSL_KEY_PATH = os.environ.get('CC_SSL_KEY_PATH', '/backend/configuration_controller/certs/device_c.key')
    SAS_CERT_PATH = os.environ.get('SAS_CERT_PATH', '')


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    pass
