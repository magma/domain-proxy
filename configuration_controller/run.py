import importlib
import logging
import os
import time

import click
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from configuration_controller.config import Config
from configuration_controller.request_consumer import request_consumer, RequestConsumer
from configuration_controller.request_formatting.merger import merge_requests
from configuration_controller.request_router.request_router import RequestRouter
from configuration_controller.response_processor import response_processor, ResponseProcessor
from db.db import DB, request_types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("configuration_controller.run")


@click.group()
def cli():
    pass


@cli.command()
def run():
    config = get_config()
    scheduler = BackgroundScheduler()
    db = DB(
        uri=config.SQLALCHEMY_DB_URI,
        encoding=config.SQLALCHEMY_DB_ENCODING,
        echo=config.SQLALCHEMY_ECHO,
        future=config.SQLALCHEMY_FUTURE
    )
    db.initialize()
    router = RequestRouter(
        sas_url=config.SAS_URL,
        rc_ingest_url=config.RC_INGEST_URL,
        cert_path=config.CC_CERT_PATH,
        ssl_key_path=config.CC_SSL_KEY_PATH,
        request_mapping_file_path=config.REQUEST_MAPPING_FILE_PATH,
        ssl_verify=config.SAS_CERT_PATH
    )
    for request_type in request_types:
        consumer = request_consumer(db=db, request_type=request_type)
        processor = response_processor(db=db, request_type=request_type)
        scheduler.add_job(
            process_requests,
            args=[consumer, processor, router],
            trigger=IntervalTrigger(
                seconds=config.REQUEST_PROCESSING_INTERVAL),
            max_instances=1,
            name=f"{request_type}_job"
        )
    scheduler.start()

    while True:
        time.sleep(1)


def get_config() -> Config:
    app_config = os.environ.get(
        'APP_CONFIG', 'configuration_controller.config.ProductionConfig')
    config_module = importlib.import_module(
        '.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])
    return config_class()


def process_requests(consumer: RequestConsumer, processor: ResponseProcessor, router: RequestRouter):
    sas_response = None
    requests_map = consumer.get_requests()
    requests_type = next(iter(requests_map))
    requests_list = requests_map[requests_type]
    if not requests_list:
        logger.debug(f"Received no {requests_type} requests.")
        return

    logger.info(
        f'Processing {len(requests_list)} {requests_type} requests')
    bulked_sas_requests = merge_requests(requests_map)
    logger.info(f"About to send {bulked_sas_requests} to SAS")
    sas_response = router.post_to_sas(bulked_sas_requests)
    logger.info(f"Received SAS response: {sas_response.json()}")
    processor.process_response(requests_list, sas_response)
    return sas_response


if __name__ == '__main__':
    run()
