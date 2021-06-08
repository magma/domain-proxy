import requests
import responses
from parameterized import parameterized

from configuration_controller.mappings.request_response_mapping import request_response
from configuration_controller.response_processor.response_db_processor import ResponseDBProcessor
from configuration_controller.response_processor.strategies.strategies_mapping import processor_strategies
from configuration_controller.tests.fixtures.fake_requests.deregistration_requests import deregistration_requests
from configuration_controller.tests.fixtures.fake_requests.grant_requests import grant_requests
from configuration_controller.tests.fixtures.fake_requests.heartbeat_requests import heartbeat_requests
from configuration_controller.tests.fixtures.fake_requests.registration_requests import registration_requests
from configuration_controller.tests.fixtures.fake_requests.relinquishment_requests import relinquishment_requests
from configuration_controller.tests.fixtures.fake_requests.spectrum_inquiry_requests import spectrum_inquiry_requests
from db_service.models import DBGrant, DBGrantState, DBRequest, DBRequestState, DBRequestType, DBResponse
from db_service.tests.db_testcase import DBTestCase
from mappings.types import GrantStates, RequestStates, RequestTypes

CBSD_SERIAL_NR = "cbsdSerialNumber"
FCC_ID = "fccId"
CBSD_ID = "cbsdId"
GRANT_ID = "grantId"


class DefaultResponseDBProcessorTestCase(DBTestCase):

    @parameterized.expand([
        (processor_strategies["registrationRequest"], registration_requests),
        (processor_strategies["spectrumInquiryRequest"], spectrum_inquiry_requests),
        (processor_strategies["grantRequest"], grant_requests),
        (processor_strategies["heartbeatRequest"], heartbeat_requests),
        (processor_strategies["relinquishmentRequest"], relinquishment_requests),
        (processor_strategies["deregistrationRequest"], deregistration_requests),
    ])
    @responses.activate
    def test_processor_splits_sas_response_into_separate_db_objects_and_links_them_with_requests(
            self, processor_strategy, requests_fixtures):

        # When
        request_type_name = self._get_request_type_from_fixture(requests_fixtures)
        response_type_name = request_response[request_type_name]
        pending_state = DBRequestState(name=RequestStates.PENDING.value)
        processed_state = DBRequestState(name=RequestStates.PROCESSED.value)
        grant_state_idle = DBGrantState(name=GrantStates.IDLE.value)
        grant_state_granted = DBGrantState(name=GrantStates.GRANTED.value)
        grant_state_authorized = DBGrantState(name=GrantStates.AUTHORIZED.value)
        request_type = DBRequestType(name=request_type_name)

        db_requests = self._create_db_requests_from_fixture(
            request_state=pending_state,
            request_type=request_type,
            fixture=requests_fixtures)
        nr_of_requests = len(db_requests)

        response_payload = self._create_response_payload_from_db_requests(
            response_type_name=response_type_name,
            db_requests=db_requests)

        any_url = 'https://foo.com/foobar'
        responses.add(responses.GET, any_url, json=response_payload, status=200)
        response = requests.get(any_url)  # url and method don't matter, I'm just crafting a qualified response here

        self.session.add_all([pending_state, processed_state])
        self.session.add_all([grant_state_idle, grant_state_granted, grant_state_authorized])
        self.session.add_all(db_requests)
        self.session.commit()

        processor = ResponseDBProcessor(
            response_type_name,
            request_map_key_func=processor_strategy["request_map_key"],
            response_map_key_func=processor_strategy["response_map_key"],
            process_responses_func=processor_strategy["process_responses"],
        )

        processor.process_response(db_requests, response, self.session)
        self.session.commit()

        # Then
        self.assertEqual(2, self.session.query(DBRequestState).count())
        self.assertEqual(1, self.session.query(DBRequestType).filter(DBRequestType.name == request_type_name).count())
        self.assertEqual(nr_of_requests, self.session.query(DBRequest).count())
        self.assertListEqual([r.id for r in db_requests], [_id for (_id, ) in self.session.query(DBResponse.id).all()])
        self.assertListEqual(["processed"]*nr_of_requests, [r.state.name for r in self.session.query(DBRequest).all()])

    @parameterized.expand([
        (processor_strategies["grantRequest"], grant_requests, 0, GrantStates.GRANTED.value),
        (processor_strategies["grantRequest"], grant_requests, 400, GrantStates.IDLE.value),
        (processor_strategies["grantRequest"], grant_requests, 401, GrantStates.IDLE.value),
        (processor_strategies["grantRequest"], grant_requests, 500, GrantStates.IDLE.value),
        (processor_strategies["heartbeatRequest"], heartbeat_requests, 0, GrantStates.AUTHORIZED.value),
        (processor_strategies["heartbeatRequest"], heartbeat_requests, 500, GrantStates.IDLE.value),
        (processor_strategies["heartbeatRequest"], heartbeat_requests, 501, GrantStates.GRANTED.value),
        (processor_strategies["heartbeatRequest"], heartbeat_requests, 502, GrantStates.IDLE.value),
        (processor_strategies["relinquishmentRequest"], relinquishment_requests, 0, GrantStates.IDLE.value),
    ])
    @responses.activate
    def test_grant_state_after_response(
            self, processor_strategy, requests_fixtures, response_code, expected_grant_state_name):

        # When
        request_type_name = self._get_request_type_from_fixture(grant_requests)
        response_type_name = request_response[request_type_name]
        pending_state = DBRequestState(name=RequestStates.PENDING.value)
        processed_state = DBRequestState(name=RequestStates.PROCESSED.value)
        grant_state_idle = DBGrantState(name=GrantStates.IDLE.value)
        grant_state_granted = DBGrantState(name=GrantStates.GRANTED.value)
        grant_state_authorized = DBGrantState(name=GrantStates.AUTHORIZED.value)
        request_type = DBRequestType(name=request_type_name)

        db_requests = self._create_db_requests_from_fixture(
            request_state=pending_state,
            request_type=request_type,
            fixture=requests_fixtures)
        nr_of_requests = len(db_requests)

        response_payload = self._create_response_payload_from_db_requests(
            response_type_name=response_type_name,
            db_requests=db_requests)

        for response_json in response_payload[response_type_name]:
            response_json["response"]["responseCode"] = response_code

        any_url = 'https://foo.com/foobar'
        responses.add(responses.GET, any_url, json=response_payload, status=200)
        response = requests.get(any_url)  # url and method don't matter, I'm just crafting a qualified response here

        self.session.add_all([pending_state, processed_state])
        self.session.add_all([grant_state_idle, grant_state_granted, grant_state_authorized])
        self.session.add_all(db_requests)
        self.session.commit()

        processor = ResponseDBProcessor(
            response_type_name,
            request_map_key_func=processor_strategy["request_map_key"],
            response_map_key_func=processor_strategy["response_map_key"],
            process_responses_func=processor_strategy["process_responses"],
        )
        processor.process_response(db_requests, response, self.session)
        self.session.commit()

        # Then
        self.assertEqual(nr_of_requests, self.session.query(DBRequest).count())
        self.assertListEqual([r.id for r in db_requests], [_id for (_id, ) in self.session.query(DBResponse.id).all()])
        self.assertListEqual(["processed"]*nr_of_requests, [r.state.name for r in self.session.query(DBRequest).all()])
        self.assertListEqual([expected_grant_state_name]*nr_of_requests,
                             [g.state.name for g in self.session.query(DBGrant).all()])

    def _generate_cbsd_id_from_request_json(self, request_payload):
        if request_payload.get(CBSD_ID, ""):
            return request_payload.get(CBSD_ID)
        else:
            return f'{request_payload.get(FCC_ID)}/{request_payload.get(CBSD_SERIAL_NR)}'

    def _get_request_type_from_fixture(self, fixture):
        return next(iter(fixture[0].keys()))

    def _create_db_requests_from_fixture(self, request_state, request_type, fixture):
        request_type_name = self._get_request_type_from_fixture(fixture)
        return [
            DBRequest(
                cbsd_id=self._generate_cbsd_id_from_request_json(r[request_type_name][0]),
                state=request_state,
                type=request_type,
                payload=r[request_type_name][0])
            for r in fixture
        ]

    def _create_response_payload_from_db_requests(self, response_type_name, db_requests):
        response_payload = {response_type_name: []}
        for db_request in db_requests:
            response_json = {"response": {"responseCode": 0}, "cbsdId": db_request.cbsd_id}
            if db_request.payload.get(GRANT_ID, ""):
                response_json[GRANT_ID] = db_request.payload.get(GRANT_ID)
            elif response_type_name == request_response[RequestTypes.GRANT.value]:
                response_json[GRANT_ID] = f'test_grant_id_for_{db_request.cbsd_id}'
            response_payload[response_type_name].append(response_json)

        return response_payload
