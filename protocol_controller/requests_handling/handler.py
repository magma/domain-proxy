import logging
from flask import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def registration():
    logger.info('Executed registration action')
    return Response(status=200, headers={})


def spectrumInquiry():
    logger.info('Executed spectrumInquiry action')
    return Response(status=200, headers={})


def grant():
    logger.info('Executed grant action')
    return Response(status=200, headers={})


def heartbeat():
    logger.info('Executed heartbeat action')
    return Response(status=200, headers={})


def relinquishment():
    logger.info('Executed relinquishment action')
    return Response(status=200, headers={})


def deregistration():
    logger.info('Executed deregistration action')
    return Response(status=200, headers={})
