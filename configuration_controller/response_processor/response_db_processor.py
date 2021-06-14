import logging
from typing import Callable, Dict, List

from requests import Response

from db_service.session_manager import Session
from db_service.models import DBRequest, DBRequestState, DBResponse
from mappings.types import RequestStates

logger = logging.getLogger(__name__)


class ResponseDBProcessor:
    def __init__(self,
                 response_type: str,
                 request_map_key_func: Callable,
                 response_map_key_func: Callable):
        self.response_type = response_type
        self.request_map_key_func = request_map_key_func
        self.response_map_key_func = response_map_key_func

    def process_response(self, requests: List[DBRequest], response: Response, session: Session) -> None:
        if not response.json():
            logger.warning(f"[{self.response_type}] Cannot update requests from SAS reply: {response.json()}")
            return

        logger.debug(f"[{self.response_type}] Processing requests: {requests} using response {response.json()}")
        self._add_responses(requests, response, session)
        self._mark_requests_as_processed(requests, session)

    def _add_responses(self, requests: List[DBRequest], response: Response, session: Session) -> None:
        requests_map = {self.request_map_key_func(req.payload): req for req in requests}
        response_json_list = response.json().get(self.response_type, [])
        logger.debug(f"[{self.response_type}] requests json list: {response_json_list}")

        for response_json in response.json().get(self.response_type, []):
            map_key = self.response_map_key_func(response_json)
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
        logger.debug(f"[{self.response_type}] Marking requests: {requests} as processed.")
        request_processed_state = session.query(DBRequestState).filter(
            DBRequestState.name == RequestStates.PROCESSED.value).scalar()
        for request in requests:
            logger.info(f"[{self.response_type}] Setting Request {request} state to {RequestStates.PROCESSED.value}.")
            request.state = request_processed_state
