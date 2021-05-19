import logging

from typing import List, Dict

from configuration_controller.custom_types.custom_types import Request
from configuration_controller.response_processor.response_processor import ResponseProcessor
from db.db import DB, Session
from db.models import DBRequest, DBRequestState, DBResponse


logger = logging.getLogger(__name__)


class ResponseDBProcessor(ResponseProcessor):
    def __init__(self, db: DB):
        self.db = db

    def process_response(self, requests: List[Request], response: str) -> None:
        if not response:
            logger.warning(
                f"[{self.response_type}] Cannot update {self.request_type} requests from SAS reply: {response}")
            return
        with self.db.session_scope() as session:
            logger.debug(
                f"[{self.response_type}] Processing requests: {requests} using response {response}")
            self._add_responses(requests, response, session)
            self._mark_requests_as_processed(requests, session)
            session.commit()

    def _add_responses(self, requests: List[Request], response: str, session: Session) -> None:
        requests_map = {self._generate_request_map_key(
            req): req for req in requests}
        response_json_list = response.json().get(self.response_type, [])
        logger.debug(
            f"[{self.response_type}] requests json list: {response_json_list}")
        for response_json in response.json().get(self.response_type, []):
            map_key = self._generate_response_map_key(response_json)
            if not map_key or map_key not in requests_map:
                logger.warning(
                    f"[{self.response_type}] Did not find {map_key} in request map {requests_map}.")
                continue
            response = DBResponse(
                response_code=int(response_json["response"]["responseCode"]),
                payload=response_json,
                request_id=requests_map[map_key].id)
            logger.info(
                f"[{self.response_type}] Adding Response: {response} for Request {requests_map[map_key]}")
            session.add(response)

    def _generate_response_map_key(self, response_json: Dict) -> str:
        return response_json.get("cbsdId", "")

    def _generate_request_map_key(self, request: Request) -> str:
        return request.cbsd_id

    def _mark_requests_as_processed(self, requests: List[Request], session: Session) -> None:
        # TODO: optimize
        logger.debug(
            f"[{self.response_type}] Marking requests: {requests} as processed.")
        processed_state_id = session.query(DBRequestState.id).filter(
            DBRequestState.name == "processed").first().id
        for request in requests:
            logger.info(
                f"[{self.response_type}] Updating Request {request} with state_id={processed_state_id}.")
            session.query(DBRequest).filter(
                DBRequest.id == request.id
            ).update(
                {
                    DBRequest.state_id: processed_state_id
                }
            )


class RegistrationResponseDBProcessor(ResponseDBProcessor):
    request_type = "registrationRequest"
    response_type = "registrationResponse"


class SpectrumInquiryDBProcessor(ResponseDBProcessor):
    request_type = "spectrumInquiryRequest"
    response_type = "spectrumInquiryResponse"


class GrantResponseDBProcessor(ResponseDBProcessor):
    request_type = "grantRequest"
    response_type = "grantResponse"


class HeartbeatResponseDBProcessor(ResponseDBProcessor):
    request_type = "heartbeatRequest"
    response_type = "heartbeatResponse"

    def _generate_response_map_key(self, response_json: Dict) -> str:
        logger.debug(
            f"Generaing response map key from response {response_json}")
        return response_json.get("cbsdId", "") + "/" + response_json.get("grantId", "")

    def _generate_request_map_key(self, request: Request) -> str:
        logger.debug(f"Generaing request map key from request {request}")
        return request.cbsd_id + "/" + request.payload["grantId"]


class RelinquishmentResponseDBProcessor(ResponseDBProcessor):
    request_type = "relinquishmentRequest"
    response_type = "relinquishmentResponse"

    def _generate_response_map_key(self, response_json: Dict) -> str:
        logger.debug(
            f"Generaing response map key from response {response_json}")
        return response_json.get("cbsdId", "") + "/" + response_json.get("grantId", "")

    def _generate_request_map_key(self, request: Request) -> str:
        logger.debug(f"Generaing request map key from request {request}")
        return request.cbsd_id + "/" + request.payload["grantId"]


class DeregistrationResponseDBProcessor(ResponseDBProcessor):
    request_type = "deregistrationRequest"
    response_type = "deregistrationResponse"
