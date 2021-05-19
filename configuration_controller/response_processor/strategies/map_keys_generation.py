import logging
from typing import Dict

logger = logging.getLogger(__name__)


_RESPONSE_MSG = f"Generaing map key from {{}}"
_CBSD_SERIAL_NR = "cbsdSerialNumber"
_FCC_ID = "fccId"
_CBSD_ID = "cbsdId"
_GRANT_ID = "grantId"


def generate_registration_request_map_key(request_json: Dict) -> str:
    logger.debug(_RESPONSE_MSG.format(request_json))
    return f'{request_json.get(_FCC_ID, "")}/{request_json.get(_CBSD_SERIAL_NR, "")}'


def generate_simple_request_map_key(request_json: Dict) -> str:
    logger.debug(_RESPONSE_MSG.format(request_json))
    return request_json.get(_CBSD_ID, "")


def generate_compound_request_map_key(request_json: Dict) -> str:
    logger.debug(_RESPONSE_MSG.format(request_json))
    return f'{request_json.get(_CBSD_ID, "")}/{request_json.get(_GRANT_ID, "")}'


def generate_simple_response_map_key(response_json: Dict) -> str:
    logger.debug(_RESPONSE_MSG.format(response_json))
    return response_json.get(_CBSD_ID, "")


def generate_compound_response_map_key(response_json: Dict) -> str:
    logger.debug(_RESPONSE_MSG.format(response_json))
    return f'{response_json.get(_CBSD_ID, "")}/{response_json.get(_GRANT_ID, "")}'
