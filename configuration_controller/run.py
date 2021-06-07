import importlib
import logging
import os
import time
from typing import Optional

import click
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from requests import Response

from configuration_controller.config import Config
from configuration_controller.mappings.request_response_mapping import request_response
from configuration_controller.request_consumer.request_consumer import RequestConsumer
from configuration_controller.request_consumer.request_db_consumer import RequestDBConsumer
from configuration_controller.request_formatting.merger import merge_requests
from configuration_controller.request_router.exceptions import RequestRouterException
from configuration_controller.request_router.request_router import RequestRouter
from configuration_controller.response_processor.response_db_processor import ResponseDBProcessor
from configuration_controller.response_processor.response_processor import ResponseProcessor
from configuration_controller.response_processor.strategies.strategies_mapping import processor_strategies
from db.db import DB
from db.models import Base
from db.types import RequestTypes
from mappings.request_mapping import request_mapping

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
    Base.metadata.create_all(db.engine)  # TODO replace with migrations
    router = RequestRouter(
        sas_url=config.SAS_URL,
        rc_ingest_url=config.RC_INGEST_URL,
        cert_path=config.CC_CERT_PATH,
        ssl_key_path=config.CC_SSL_KEY_PATH,
        request_mapping=request_mapping,
        ssl_verify=config.SAS_CERT_PATH
    )
    for request_type in RequestTypes:
        req_type = request_type.value
        response_type = request_response[req_type]
        consumer = RequestDBConsumer(db=db, request_type=req_type)
        processor = ResponseDBProcessor(
            db=db,
            response_type=response_type,
            response_map_key_func=processor_strategies[req_type]["response_map_key"],
        )
        scheduler.add_job(
            process_requests,
            args=[consumer, processor, router],
            trigger=IntervalTrigger(
                seconds=config.REQUEST_PROCESSING_INTERVAL),
            max_instances=1,
            name=f"{req_type}_job"
        )
    scheduler.start()

    while True:
        time.sleep(1)


def get_config() -> Config:
    app_config = os.environ.get('APP_CONFIG', 'configuration_controller.config.ProductionConfig')
    config_module = importlib.import_module('.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])
    return config_class()


def process_requests(
        consumer: RequestConsumer,
        processor: ResponseProcessor,
        router: RequestRouter) -> Optional[Response]:

    requests_map = consumer.get_pending_requests()
    requests_type = next(iter(requests_map))
    requests_list = requests_map[requests_type]

    if not requests_list:
        logger.debug(f"Received no {requests_type} requests.")
        return

    logger.info(f'Processing {len(requests_list)} {requests_type} requests')
    bulked_sas_requests = merge_requests(requests_map)

    try:
        sas_response = router.post_to_sas(bulked_sas_requests)
        logger.info(f"Sent {bulked_sas_requests} to SAS and got the following response: {sas_response.json()}")
    except RequestRouterException as e:
        logging.error(f"Error posting request to SAS: {e}")
        return

    processor.process_response(requests_list, sas_response)
    return sas_response


if __name__ == '__main__':
    run()
