import json

import testing.postgresql
from parameterized import parameterized

from db_service.db_initialize import DBInitializer
from db_service.models import DBRequest, DBResponse
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from radio_controller.service.service import RadioControllerService

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


class RadioControllerTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.rc_service = RadioControllerService(SessionManager(self.engine))
        DBInitializer(SessionManager(self.engine)).initialize()

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

    def test_store_requests_from_map_stores_requests_in_db(self):
        # Given
        request_map = {
             "registrationRequest": [{"fccId": "foo1", "cbsdSerialNumber": "foo2"},
                                     {"fccId": "foo1", "cbsdSerialNumber": "foo2"}]
         }

        # When
        self.rc_service._store_requests_from_map(request_map)
        db_request_ids = self.session.query(DBRequest.id).all()
        db_request_ids = [_id for (_id,) in db_request_ids]

        # Then
        self.assertListEqual(db_request_ids, [1, 2])
