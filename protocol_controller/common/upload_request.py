import json
import logging

from protocol_controller.grpc_client.grpc_client import GrpcClient
from requests_pb2 import RequestPayload, RequestDbIds, ResponsePayload


def upload_request(client: GrpcClient, request_type: str, request_payload: str) -> ResponsePayload:
    req = RequestPayload(payload=json.dumps(request_payload))
    grpc_response = client.Upload(req)
    logging.info(f'Executed {request_type} action. GRPC response: {grpc_response.msg}')
    return grpc_response
