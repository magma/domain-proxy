import logging

from requests import Response
from typing import List, Dict, Callable

from configuration_controller.response_processor.response_processor import ResponseProcessor
from db.db import DB, Session
from db.models import DBRequest, DBRequestState, DBResponse
from db.types import RequestStates

logger = logging.getLogger(__name__)


class ResponseDBProcessor(ResponseProcessor):
    def __init__(self,
                 db: DB,
                 response_type: str,
                 response_map_key_func: Callable):
        self.db = db
        self.response_type = response_type
        self.response_map_key_func = response_map_key_func

    def process_response(self, requests: List[DBRequest], response: Response) -> None:
        if not response.json():
            logger.warning(f"[{self.response_type}] Cannot update requests from SAS reply: {response.json()}")
            return
        with self.db.session_scope() as session:
            logger.debug(f"[{self.response_type}] Processing requests: {requests} using response {response.json()}")
            self._add_responses(requests, response, session)
            self._mark_requests_as_processed(requests, session)
            session.commit()

    def _add_responses(self, requests: List[DBRequest], response: Response, session: Session) -> None:
        requests_map = {req.cbsd_id: req for req in requests}
        response_json_list = response.json().get(self.response_type, [])
        logger.debug(f"[{self.response_type}] requests json list: {response_json_list}")

        for response_json in response.json().get(self.response_type, []):
            map_key = self._generate_response_map_key(response_json)
            if not map_key or map_key not in requests_map:
                logger.warning(f"[{self.response_type}] Did not find {map_key} in request map {requests_map}.")
                continue
            db_response = DBResponse(
                response_code=int(response_json["response"]["responseCode"]),
                payload=response_json,
                request_id=requests_map[map_key].id)
            logger.info(f"[{self.response_type}] Adding Response: {db_response} for Request {requests_map[map_key]}")
            session.add(db_response)

    def _generate_response_map_key(self, response_json: Dict) -> str:
        return self.response_map_key_func(response_json)

    def _mark_requests_as_processed(self, requests: List[DBRequest], session: Session) -> None:
        # TODO: optimize
        logger.debug(f"[{self.response_type}] Marking requests: {requests} as processed.")
        processed_state_id = session.query(DBRequestState.id).filter(
            DBRequestState.name == RequestStates.PROCESSED.value).first().id
        for request in requests:
            logger.info(f"[{self.response_type}] Updating Request {request} with state_id={processed_state_id}.")
            session.query(DBRequest).filter(
                DBRequest.id == request.id
            ).update(
                {
                    DBRequest.state_id: processed_state_id
                }
            )
