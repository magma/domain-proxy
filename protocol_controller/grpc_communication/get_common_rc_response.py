import json
import logging
from datetime import datetime, timedelta
from time import sleep
from typing import OrderedDict, Dict, Optional

from flask import current_app, Request
from grpc import RpcError
from werkzeug.exceptions import BadRequest

from protocol_controller.grpc_client.grpc_client import GrpcClient
from protocol_controller.grpc_communication.upload_request import upload_requests
from requests_pb2 import RequestDbId


# TODO Perhaps all of the below functions could be moved to the GrpcClient class or its subclass

def get_common_bulk_rc_response(request: Request, response_name: str):
    client = current_app.extensions["GrpcClient"]
    try:
        req_db_ids = upload_requests(client, json.dumps(request.json))
        responses_dict = collect_rc_responses(client, req_db_ids)
    except RpcError as e:
        raise BadRequest(str(e))
    resp = {response_name: list(responses_dict.values())}  # TODO validate with marshmallow or sth
    return resp, 200


def collect_rc_responses(client: GrpcClient, req_db_ids) -> OrderedDict[int, Dict]:
    responses_dict = OrderedDict.fromkeys(req_db_ids, None)
    for _id in responses_dict:  # TODO definitely do it asynchronously!!!!! This can only serve as a PoC
        start = datetime.now()
        while datetime.now() < start + timedelta(seconds=current_app.config["RC_RESPONSE_WAIT_TIMEOUT"]):
            try:
                resp = check_response_for_id(client, _id)
            except RpcError as e:
                logging.warning(f"Unable to get response from Radio Controller for request {_id}. Reason: {e}")
                break

            if resp:
                responses_dict[_id] = resp
                break
            else:
                sleep(current_app.config["RC_RESPONSE_WAIT_INTERVAL"])

    return responses_dict


def check_response_for_id(client: GrpcClient, req_id: int) -> Optional[Dict]:
    req = RequestDbId(id=req_id)
    grpc_response = client.GetResponse(req)
    response_dict = json.loads(grpc_response.payload)
    logging.info(f'SAS response for request {req_id}: {response_dict}')
    return response_dict
