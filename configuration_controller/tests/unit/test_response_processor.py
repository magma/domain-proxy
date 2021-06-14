import requests
import responses

from configuration_controller.response_processor.response_db_processor import (
    ResponseDBProcessor,
)
from configuration_controller.response_processor.strategies.map_keys_generation import (
    generate_registration_request_map_key,
    generate_simple_response_map_key,
)
from configuration_controller.tests.fixtures.fake_requests.registration_requests import (
    registration_requests,
)
from db_service.models import DBRequest, DBRequestState, DBRequestType, DBResponse
from db_service.tests.db_testcase import DBTestCase


class DefaultResponseDBProcessorTestCase(DBTestCase):

    @responses.activate
    def test_processor_splits_sas_response_into_separate_db_objects_and_links_them_with_requests(self):
        # When
        pending_state = DBRequestState(name="pending")
        processed_state = DBRequestState(name="processed")
        req_type = DBRequestType(name="registrationRequest")

        reqs = [
            DBRequest(cbsd_id=f'{r["registrationRequest"][0]["fccId"]}/{r["registrationRequest"][0]["cbsdSerialNumber"]}',
                      state=pending_state,
                      type=req_type,
                      payload=r["registrationRequest"][0])
            for r in registration_requests
        ]

        cbsd_id_1 = reqs[0].cbsd_id
        cbsd_id_2 = reqs[1].cbsd_id
        any_url = 'https://foo.com/foobar'
        resp_payload = {
            "registrationResponse": [
                {"response": {"responseCode": 0}, "cbsdId": cbsd_id_1},
                {"response": {"responseCode": 0}, "cbsdId": cbsd_id_2}
            ]
        }
        responses.add(responses.GET, any_url, json=resp_payload, status=200)
        response = requests.get(any_url)  # url and method don't matter, I'm just crafting a qualified response here

        self.session.add_all([pending_state, processed_state])
        self.session.add_all(reqs)
        self.session.commit()

        processor = ResponseDBProcessor(
            "registrationResponse",
            request_map_key_func=generate_registration_request_map_key,
            response_map_key_func=generate_simple_response_map_key,
        )

        # When
        processor.process_response(reqs, response, self.session)
        self.session.commit()

        # Then
        self.assertEqual(2, self.session.query(DBRequestState).count())
        self.assertEqual(1, self.session.query(DBRequestType).count())
        self.assertEqual(2, self.session.query(DBResponse).count())
        self.assertListEqual([reqs[0].id, reqs[1].id], [_id for (_id, ) in self.session.query(DBResponse.id).all()])
        self.assertEqual("processed", reqs[0].state.name)
        self.assertEqual("processed", reqs[1].state.name)
