import importlib
import logging
import os
import time

import click
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from configuration_controller.config import Config
from configuration_controller.consumer.consumer import RequestsConsumer
from configuration_controller.request_formatting.merger import merge_requests
from configuration_controller.request_router.request_router import RequestRouter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def run():
    config = get_config()
    scheduler = BackgroundScheduler()
    consumer = RequestsConsumer()
    router = RequestRouter(
        sas_url=config.SAS_URL,
        rc_ingest_url=config.RC_INGEST_URL,
        cert_path=config.CC_CERT_PATH,
        ssl_key_path=config.CC_SSL_KEY_PATH,
        request_mapping_file_path=config.REQUEST_MAPPING_FILE_PATH,
        ssl_verify=config.SAS_CERT_PATH
    )
    scheduler.add_job(
        process_requests,
        args=[consumer, router],
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


def process_requests(consumer, router):
    logger.info('Processing requests')
    sas_responses = []
    sas_requests = consumer.process_db_requests()
    for req in consumer.request_list:
        requests_list = sas_requests.get(req)
        if not requests_list:
            continue
        bulked_sas_requests = merge_requests(sas_requests[req])
        sas_response = router.post_to_sas(bulked_sas_requests)
        sas_responses.append(sas_response)
        logger.info(f'{sas_response.json()=}')
    return sas_responses


if __name__ == '__main__':
    run()
