import importlib
import logging
import os
from concurrent import futures
from signal import signal, SIGTERM

import grpc

from requests_pb2_grpc import add_RadioControllerServicer_to_server

from radio_controller.config import Config
from radio_controller.service import RadioControllerService


def run():
    logging.info("Starting grpc server")
    config = get_config()
    logging.info(f"grpc port is: {config.GRPC_PORT}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_RadioControllerServicer_to_server(
        RadioControllerService(), server
    )
    server.add_insecure_port(f"[::]:{config.GRPC_PORT}")
    server.start()
    logging.info(f"GRPC Server started on port {config.GRPC_PORT}")

    def handle_sigterm(*_):
        logging.info("Received shutdown signal")
        all_rpcs_done_event = server.stop(30)
        all_rpcs_done_event.wait(30)
        logging.info("Shut down gracefully")

    signal(SIGTERM, handle_sigterm)
    server.wait_for_termination()


def get_config() -> Config:
    app_config = os.environ.get('APP_CONFIG', 'radio_controller.config.ProductionConfig')
    config_module = importlib.import_module('.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])
    logging.info(str(config_class))
    return config_class()


if __name__ == "__main__":
    run()
