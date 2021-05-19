from configuration_controller.request_consumer.request_db_consumer import (
    RequestDBConsumer,
)
from db.models import DBRequest, DBRequestState, DBRequestType
from db.tests.db_testcase import DBTestCase


class RegistrationDBConsumerTestCase(DBTestCase):

    def test_get_pending_requests_retrieves_empty_list_of_requests_when_no_pending_requests_in_db(self):
        # Given
        consumer = RequestDBConsumer("someRequest")

        # When
        reqs = consumer.get_pending_requests(self.session)

        # Then
        self.assertEqual(0, len(list(reqs.values())[0]))

    def test_get_pending_requests_retrieves_pending_requests_only(self):
        # Given
        consumer = RequestDBConsumer("someRequest")
        req_type = DBRequestType(name="someRequest")
        pending_status = DBRequestState(name="pending")
        processed_status = DBRequestState(name="processed")
        req1 = DBRequest(cbsd_id="foo1", type=req_type, state=pending_status, payload={"some": "payload1"})
        req2 = DBRequest(cbsd_id="foo2", type=req_type, state=pending_status, payload={"some": "payload2"})
        req3 = DBRequest(cbsd_id="foo3", type=req_type, state=processed_status, payload={"some": "payload3"})
        self.session.add_all([req1, req2, req3])
        self.session.commit()

        # When
        reqs = consumer.get_pending_requests(self.session)

        # Then
        self.assertEqual(2, len(list(reqs.values())[0]))
