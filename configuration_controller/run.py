import importlib
import logging
import os
import time

import click
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from configuration_controller.config import Config


@click.group()
def cli():
    pass


@cli.command()
@click.option("--msg", "-m")
def run(msg):
    config = get_config()
    logging.basicConfig(level=config.LOG_LEVEL)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        hello_job,
        args=[msg],
        trigger=IntervalTrigger(seconds=config.REQUEST_PROCESSING_INTERVAL),
        max_instances=1,
    )
    scheduler.start()

    while True:
        time.sleep(1)


def get_config() -> Config:
    app_config = os.environ.get('APP_CONFIG', 'configuration_controller.config.ProductionConfig')
    config_module = importlib.import_module('.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])
    return config_class()


def hello_job(msg):
    logging.debug(msg)
    print(msg)


if __name__ == '__main__':
    run()
