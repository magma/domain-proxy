import json
import logging
from typing import Dict, List, Optional

from db_service.models import DBRequest, DBRequestState, DBRequestType, DBResponse
from db_service.session_manager import SessionManager
from mappings.types import RequestStates
from radio_controller.service.strategies.strategies_mapping import get_cbsd_id_strategies
from requests_pb2 import RequestDbId, RequestDbIds, RequestPayload, ResponsePayload
from requests_pb2_grpc import RadioControllerServicer

logger = logging.getLogger(__name__)

CBSD_SERIAL_NR = "cbsdSerialNumber"
FCC_ID = "fccId"
CBSD_ID = "cbsdId"


class RadioControllerService(RadioControllerServicer):
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def UploadRequests(self, request_payload: RequestPayload, context) -> RequestDbIds:
        """Method to insert requests to the database"""
        logger.info("Storing requests in DB.")
        requests_map = json.loads(request_payload.payload)
        db_request_ids = self._store_requests_from_map(requests_map)
        return RequestDbIds(ids=db_request_ids)

    def GetResponse(self, pb2_message: RequestDbId, context) -> ResponsePayload:
        """Method to retrieve response for given request"""
        logger.info(f"Getting SAS response for request {pb2_message.id}")
        response = self._get_request_response(pb2_message.id)
        if response.payload:
            logger.info(f"Returning response {response.payload} for request id: {pb2_message.id}.")

        return response

    def _store_requests_from_map(self, request_map: Dict[str, List[Dict]]) -> List[int]:
        request_db_ids = []
        request_type = next(iter(request_map))
        with self.session_manager.session_scope() as session:
            request_pending_state = session.query(DBRequestState).filter(
                DBRequestState.name == RequestStates.PENDING.value).scalar()
            req_type = session.query(DBRequestType).filter(DBRequestType.name == request_type).scalar()
            for request_json in request_map[request_type]:
                db_request = DBRequest(
                    type=req_type,
                    state=request_pending_state,
                    cbsd_id=self.get_cbsd_id(request_type, request_json),
                    payload=request_json
                )
                if db_request:
                    logger.info(f"Adding request {db_request}.")
                    session.add(db_request)
                    session.flush()
                    request_db_ids.append(db_request.id)
            session.commit()
        return request_db_ids

    def _get_request_response(self, request_db_id: int) -> ResponsePayload:
        with self.session_manager.session_scope() as session:
            logger.info(f"Trying to fetch DB response for request id: {request_db_id}")
            response = session.query(DBResponse).filter(DBResponse.request_id == request_db_id).first()
        if not response:
            return ResponsePayload(payload='{}')
        return ResponsePayload(payload=json.dumps(response.payload))

    @staticmethod
    def get_cbsd_id(request_name: str, request_payload: Dict):
        return get_cbsd_id_strategies[request_name](request_payload)
