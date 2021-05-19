import json
import logging
from typing import Dict, List, Optional

from requests_pb2 import RequestDbId, RequestDbIds, RequestPayload, ResponsePayload
from requests_pb2_grpc import RadioControllerServicer

from db.db import DB
from db.models import DBRequest, DBRequestState, DBRequestType, DBResponse
from db.types import RequestStates

logger = logging.getLogger(__name__)


CBSD_SERIAL_NR = "cbsdSerialNumber"
FCC_ID = "fccId"
CBSD_ID = "cbsdId"


class RadioControllerService(RadioControllerServicer):
    def __init__(self, db: DB):
        self.db = db

    def UploadRequests(self, request_payload: RequestPayload, context) -> RequestDbIds:
        """Method to insert requests to the database"""
        logger.info("Storing requests in DB.")
        requests_map = json.loads(request_payload.payload)
        db_request_ids = self._store_requests_from_map(requests_map) or []
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
        try:
            request_type = next(iter(request_map))
        except (StopIteration, TypeError) as e:
            logger.error(f"Incorrect request map format: {request_map}. Details: {e}")
            return []
        with self.db.session_scope() as session:
            request_pending_state = session.query(DBRequestState).filter(
                DBRequestState.name == RequestStates.PENDING.value).scalar()
            req_type = session.query(DBRequestType).filter(
                DBRequestType.name == request_type).scalar()
            for request_json in request_map[request_type]:
                db_request = self._create_db_request(
                    request_type=req_type,
                    request_state=request_pending_state,
                    request_payload=request_json
                )
                if db_request:
                    logger.info(f"Adding request {db_request}.")
                    session.add(db_request)
                    session.flush()
                    request_db_ids.append(db_request.id)
                else:
                    request_db_ids.append(0)
            session.commit()
        return request_db_ids

    @staticmethod
    def _create_db_request(request_type: DBRequestType,
                           request_state: DBRequestState,
                           request_payload: Dict) -> Optional[DBRequest]:
        cbsd_id = None

        if FCC_ID in request_payload and CBSD_SERIAL_NR in request_payload:
            cbsd_id = f'{request_payload[FCC_ID]}/{request_payload[CBSD_SERIAL_NR]}'

        elif CBSD_ID in request_payload:
            cbsd_id = request_payload[CBSD_ID]

        if not cbsd_id:
            logger.error(f"Could not generate cbsd_id from request: {request_payload}.")
            return None
        return DBRequest(
            type=request_type,
            state=request_state,
            cbsd_id=cbsd_id,
            payload=request_payload)

    def _get_request_response(self, request_db_id: int) -> ResponsePayload:
        with self.db.session_scope() as session:
            logger.info(f"Trying to fetch DB response for request id: {request_db_id}")
            response = session.query(DBResponse).filter(DBResponse.request_id == request_db_id).first()
        if not response:
            return ResponsePayload(payload='{}')
        return ResponsePayload(payload=json.dumps(response.payload))
