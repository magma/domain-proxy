import requests
import responses

from configuration_controller.response_processor.response_db_processor import ResponseDBProcessor
from configuration_controller.response_processor.strategies.map_keys_generation import generate_simple_response_map_key
from db.models import DBRequest, DBRequestState, DBRequestType, DBResponse
from db.tests.db_testcase import DBTestCase


class DefaultResponseDBProcessorTestCase(DBTestCase):

    @responses.activate
    def test_processor_splits_sas_response_into_separate_db_objects_and_links_them_with_requests(self):
        # When
        cbsd_id_1 = "foo1"
        cbsd_id_2 = "foo2"
        any_url = 'https://foo.com/foobar'
        resp_payload = {
            "registrationResponse": [
                {"response": {"responseCode": 0}, "cbsdId": cbsd_id_1},
                {"response": {"responseCode": 0}, "cbsdId": cbsd_id_2}
            ]
        }
        responses.add(responses.GET, any_url, json=resp_payload, status=200)
        response = requests.get(any_url)  # url and method don't matter, I'm just crafting a qualified response here

        pending_state = DBRequestState(name="pending")
        processed_state = DBRequestState(name="processed")
        req_type = DBRequestType(name="registrationRequest")

        req1 = DBRequest(id=1, cbsd_id=cbsd_id_1, state=pending_state, type=req_type)
        req2 = DBRequest(id=2, cbsd_id=cbsd_id_2, state=pending_state, type=req_type)

        self.session.add_all([req1, req2, processed_state])
        self.session.commit()

        processor = ResponseDBProcessor(
            self.db,
            "registrationResponse",
            response_map_key_func=generate_simple_response_map_key,
        )
        sas_request_1 = DBRequest(id=1, cbsd_id="foo1", payload={})
        sas_request_2 = DBRequest(id=2, cbsd_id="foo2", payload={})

        # When
        processor.process_response([sas_request_1, sas_request_2], response)

        # Then
        self.assertEqual(2, self.session.query(DBResponse).count())
        self.assertListEqual([req1.id, req2.id], [_id for (_id, ) in self.session.query(DBResponse.id).all()])
        self.assertEqual("processed", req1.state.name)
        self.assertEqual("processed", req2.state.name)
