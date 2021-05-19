import json
import logging

from typing import List, Dict

from db.db import DB, request_states
from db.models import DBRequest, DBRequestState, DBRequestType, DBResponse
from requests_pb2 import RequestDbId, RequestDbIds, RequestPayload, ResponsePayload
from requests_pb2_grpc import RadioControllerServicer


logger = logging.getLogger(__name__)


class RadioControllerService(RadioControllerServicer):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.pending_state = request_states[request_states.index("pending")]

    def UploadRequests(self, request_payload: RequestPayload, context):
        logger.info("Storing requests in DB.")
        requests_map = self._create_request_map_from_request_payload(request_payload)
        db_request_ids = self._store_requests_from_map(requests_map)
        return RequestDbIds(ids=db_request_ids)

    def GetResponse(self, pb2_message: RequestDbId, context):
        """Method to retrieve response for given request"""
        logger.info(f"Getting SAS response for request {pb2_message.id}")
        response_payload = self._get_request_response(pb2_message)
        if response_payload:
            logger.info(
                f"Returning response {response_payload} for request id: {pb2_message.id}.")

        return response_payload

    def _create_request_map_from_request_payload(self, request_payload: RequestPayload) -> Dict[str, List[Dict]]:
        request_json = json.loads(request_payload.payload)
        if not request_json or len(request_json) > 1:
            logger.warning(
                f"Received invalid requests JSON object: {request_json}")
            return {}
        request_type = next(iter(request_json))
        request_payload_list = [req for req in request_json[request_type]]
        return {request_type: request_payload_list}

    def _store_requests_from_map(self, request_map: Dict[str, List[Dict]]) -> List[int]:
        request_db_ids = []
        request_type = next(iter(request_map))
        with self.db.session_scope() as session:
            request_pending_state_id = session.query(DBRequestState).filter(
                DBRequestState.name == self.pending_state).first().id
            request_type_id = session.query(DBRequestType).filter(
                DBRequestType.name == request_type).first().id
            for request_json in request_map[request_type]:
                db_request = self._create_db_request(
                    request_type_id=request_type_id,
                    request_state_id=request_pending_state_id,
                    request_payload=request_json)
                session.add(db_request)
                session.flush()
                session.refresh(db_request)
                logger.info(f"Adding request {db_request}.")
                request_db_ids.append(db_request.id)
            session.commit()
        return request_db_ids

    def _create_db_request(self, request_type_id: int, request_state_id: int, request_payload: Dict) -> DBRequest:
        if "fccId" in request_payload and "cbsdSerialNumber" in request_payload:
            cbsd_id = "/".join([request_payload["fccId"],
                               request_payload["cbsdSerialNumber"]])
        elif "cbsdId" in request_payload:
            cbsd_id = request_payload["cbsdId"]
        else:
            logger.error(
                f"Count not generate cbsd_id from request: {request_payload}.")
            cbsd_id = ""
        request = DBRequest(
            type_id=request_type_id,
            state_id=request_state_id,
            cbsd_id=cbsd_id,
            payload=request_payload)
        return request

    def _get_request_response(self, request_db_id: RequestDbId) -> ResponsePayload:
        response = None
        with self.db.session_scope() as session:
            logger.info(f"Trying to fetch DB response for request id: {request_db_id.id}")
            response = session.query(
                DBResponse).filter(DBResponse.request_id==request_db_id.id).first()
        if not response:
            return ResponsePayload(payload='{}')
        return ResponsePayload(payload=json.dumps(response.payload))
