import json

import testing.postgresql
from parameterized import parameterized

from db.models import DBRequestType, DBRequestState, DBRequest, DBResponse
from radio_controller.service import RadioControllerService
from db.tests.db_testcase import DBTestCase

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


CBSD_ID = "cbsdId"


class RadioControllerTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.rc_service = RadioControllerService(self.db)

    @parameterized.expand([
        ({CBSD_ID: 1, "some_key": "some_value"}, 1, DBRequest),
        ({"definitelyNotcbsdId": 1, "some_key": "some_value"}, 0, type(None)),
    ])
    def test_create_db_request_inserts_requests_to_db_when_cbsdId_argument_present_in_payload(
            self, payload, expected, result_type
    ):
        # Given
        foo_type = DBRequestType(id=1, name="foo_type")
        foo_state = DBRequestState(id=1, name="foo_state")
        self.session.add_all([foo_type, foo_state])
        self.session.commit()

        # When
        result = self.rc_service._create_db_request(foo_type, foo_state, payload)

        requests = self.session.query(DBRequest).all()

        # Then
        self.assertEqual(expected, len(requests))
        self.assertIsInstance(result, result_type)

    @parameterized.expand([
        (1, {"foo": "bar"}, {"foo": "bar"}),
        (2, {"foo": "bar"}, {}),
    ])
    def test_get_request_response(self, req_id, db_response_payload, grpc_expected_response_payload):
        # Given
        db_request = DBRequest(id=1, cbsd_id="foo1")
        db_response = DBResponse(id=1, request_id=1, response_code=0, payload=db_response_payload)

        self.session.add_all([db_request, db_response])
        self.session.commit()

        # When
        grpc_response_payload = json.loads(self.rc_service._get_request_response(req_id).payload)

        # Then
        self.assertEqual(grpc_expected_response_payload, grpc_response_payload)

    @parameterized.expand([
        ({"registrationRequest": [{"cbsdId": "foo1"}, {"cbsdId": "foo2"}]}, [1, 2], [1, 2]),
        ({"registrationRequest": [{"cbsdId": "foo1"}, {"someId": "foo2"}]}, [1, ], [1, 0]),
        ({}, [], []),
        (None, [], []),
    ])
    def test_store_requests_from_map_stores_requests_in_db(
            self, request_map, expected_db_ids, expected_ids_returned_by_store_requests_from_map_method
    ):
        # Given
        request_map = request_map

        # When
        response_ids = self.rc_service._store_requests_from_map(request_map)
        db_request_ids = self.session.query(DBRequest.id).all()
        db_request_ids = [_id for (_id,) in db_request_ids]

        # Then
        self.assertListEqual(db_request_ids, expected_db_ids)
        self.assertListEqual(response_ids, expected_ids_returned_by_store_requests_from_map_method)
