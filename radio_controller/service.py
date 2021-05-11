import logging

from requests_pb2 import RequestPayloadResponse
from requests_pb2_grpc import RadioControllerServicer

from radio_controller.logger import logger

logging.basicConfig(level=logging.INFO)


class RadioControllerService(RadioControllerServicer):
    def Upload(self, request, context):
        logger.info(f"Uploading {request.payload_type} request to the DB")
        logger.info(request.payload)
        return RequestPayloadResponse(msg=request.payload)
