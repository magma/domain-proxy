import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from time import sleep
from typing import Dict, Optional

from flask import current_app, Request
from grpc import RpcError
from werkzeug.exceptions import BadRequest

from protocol_controller.grpc_client.grpc_client import GrpcClient
from protocol_controller.grpc_communication.upload_request import upload_requests
from requests_pb2 import RequestDbId


def get_common_bulk_rc_response(request: Request, response_name: str):
    client = current_app.extensions["GrpcClient"]
    try:
        req_db_ids = upload_requests(client, json.dumps(request.json))
        responses_dict = collect_rc_responses(client, req_db_ids)
    except RpcError as e:
        raise BadRequest(str(e))
    resp = {response_name: list(responses_dict.values())}  # TODO validate with marshmallow or sth
    return resp, 200


def collect_rc_responses(client: GrpcClient, req_db_ids) -> Dict[int, Dict]:
    timeout = current_app.config["RC_RESPONSE_WAIT_TIMEOUT"]
    with ThreadPoolExecutor() as executor:
        responses_dict = dict(
            zip(req_db_ids, executor.map(lambda _id: check_response_for_id(client, _id, timeout), req_db_ids))
        )

    return responses_dict


def check_response_for_id(client: GrpcClient, req_id: int, timeout: int) -> Optional[Dict]:
    req = RequestDbId(id=req_id)
    start = datetime.now()
    while datetime.now() < start + timedelta(seconds=timeout):
        try:
            grpc_response = client.GetResponse(req)
        except RpcError as e:
            logging.error(f"Unable to get response from Radio Controller for request {req_id}. Reason: {e}")
            return {}

        if grpc_response.payload:
            return grpc_response.payload
        else:
            sleep(current_app.config["RC_RESPONSE_WAIT_INTERVAL"])

    logging.error(f"Timed out while waiting for SAS response for request: {req_id}")
    return {}
