from typing import Type

from flask import Flask
from flask_testing import TestCase

from protocol_controller import config
from protocol_controller.config import Config
from protocol_controller.plugins.cbsd_sas.app import create_app


class AppTestCase(TestCase):
    conf: Type[Config] = config.TestConfig()

    def create_app(self) -> Flask:
        app = create_app(self.conf)
        return app
