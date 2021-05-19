import grpc
import importlib
import logging
import os

from concurrent import futures
from signal import signal, SIGTERM

from db.db import DB
from db.models import Base
from radio_controller.config import Config
from radio_controller.service import RadioControllerService
from requests_pb2_grpc import add_RadioControllerServicer_to_server


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("radio_controller.run")


def run():
    logger.info("Starting grpc server")
    config = get_config()
    logger.info(f"grpc port is: {config.GRPC_PORT}")
    db = DB(
        uri=config.SQLALCHEMY_DB_URI,
        encoding=config.SQLALCHEMY_DB_ENCODING,
        echo=config.SQLALCHEMY_ECHO,
        future=config.SQLALCHEMY_FUTURE
    )
    Base.metadata.create_all(db.engine)  # TODO replace with migrations
    db.initialize()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_RadioControllerServicer_to_server(
        RadioControllerService(db=db), server
    )
    server.add_insecure_port(f"[::]:{config.GRPC_PORT}")
    server.start()
    logger.info(f"GRPC Server started on port {config.GRPC_PORT}")

    def handle_sigterm(*_):
        logger.info("Received shutdown signal")
        all_rpcs_done_event = server.stop(30)
        all_rpcs_done_event.wait(30)
        logger.info("Shut down gracefully")

    signal(SIGTERM, handle_sigterm)
    server.wait_for_termination()


def get_config() -> Config:
    app_config = os.environ.get('APP_CONFIG', 'radio_controller.config.ProductionConfig')
    config_module = importlib.import_module('.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])
    logger.info(str(config_class))

    return config_class()


if __name__ == "__main__":
    run()
