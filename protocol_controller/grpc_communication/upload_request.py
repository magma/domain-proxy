import logging
from grpc import RpcError
from typing import List, Optional

from protocol_controller.grpc_client.grpc_client import GrpcClient
from requests_pb2 import RequestPayload


# TODO Perhaps all of the below functions could be moved to the GrpcClient class or its subclass

def upload_requests(client: GrpcClient, payload: str) -> Optional[List[int]]:
    grpc_req = RequestPayload(payload=payload)
    grpc_response = client.UploadRequests(grpc_req)
    req_db_ids = grpc_response.ids
    logging.info(f'Executed upload_requests action. GRPC response: {req_db_ids}')
    return req_db_ids
