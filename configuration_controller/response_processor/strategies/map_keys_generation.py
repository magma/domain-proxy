import logging
from typing import Dict


logger = logging.getLogger(__name__)


RESPONSE_MSG = f"Generaing response map key from response {{}}"


def generate_simple_response_map_key(response_json: Dict) -> str:
    logger.debug(RESPONSE_MSG.format(response_json))
    return response_json.get("cbsdId", "")


def generate_compound_response_map_key(response_json: Dict) -> str:
    logger.debug(RESPONSE_MSG.format(response_json))
    return f'{response_json.get("cbsdId", "")}/{response_json.get("grantId", "")}'
