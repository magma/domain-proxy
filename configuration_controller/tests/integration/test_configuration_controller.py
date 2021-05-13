import unittest

CORRECT_CERT_PATH = '/backend/configuration_controller/certs/root_ca.cert'
INCORRECT_CERT_PATH = '/backend/configuration_controller/certs/device_b_ca.cert'
NONEXISTENT_CERT_PATH = '/nonexistent/cert/path.cert'


class ConfigurationControllerTestCase(unittest.TestCase):
    """Need to write new tests once the db is in place"""
    pass
