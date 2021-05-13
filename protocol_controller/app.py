from typing import Type
from flask import Flask

from protocol_controller import config
from protocol_controller.config import Config
from protocol_controller.logger import configure_logger
from protocol_controller.views.deregistration import deregistration_page
from protocol_controller.views.grant import grant_page
from protocol_controller.views.heartbeat import heartbeat_page
from protocol_controller.views.registration import registration_page
from protocol_controller.views.relinquishment import relinquishment_page
from protocol_controller.views.spectrum_inquiry import spectrum_inquiry_page


def create_app(conf: Type[Config]):
    app = Flask(__name__)
    app.config.from_object(conf)
    configure_logger(conf)
    register_pc_blueprints(app)
    return app


def create_app_with_production_config():
    app = create_app(config.ProductionConfig)
    return app


def register_pc_blueprints(app):
    blueprints = [
        registration_page,
        spectrum_inquiry_page,
        grant_page,
        heartbeat_page,
        relinquishment_page,
        deregistration_page,
    ]
    register_blueprints(app, blueprints, app.config['API_PREFIX'])


def register_blueprints(app, blueprints, url_prefix):
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
