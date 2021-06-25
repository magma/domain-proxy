from parameterized import parameterized

from configuration_controller.request_consumer.request_db_consumer import RequestDBConsumer
from db_service.models import DBRequest, DBRequestState, DBRequestType
from db_service.session_manager import Session
from db_service.tests.db_testcase import DBTestCase


DEFAULT_MAX_REQUEST_BATCH_SIZE = 10


class RegistrationDBConsumerTestCase(DBTestCase):

    def test_get_pending_requests_retrieves_empty_list_of_requests_when_no_pending_requests_in_db(self):
        # Given
        consumer = RequestDBConsumer("someRequest", request_max_batch_size=DEFAULT_MAX_REQUEST_BATCH_SIZE)

        # When
        reqs = consumer.get_pending_requests(self.session)

        # Then
        self.assertEqual(0, len(list(reqs.values())[0]))

    def test_get_pending_requests_retrieves_pending_requests_only(self):
        # Given
        consumer = RequestDBConsumer("someRequest", request_max_batch_size=DEFAULT_MAX_REQUEST_BATCH_SIZE)

        self._prepare_two_pending_and_one_processed_request()

        # When
        reqs = consumer.get_pending_requests(self.session)

        # Then
        self.assertEqual(2, len(list(reqs.values())[0]))

    @parameterized.expand([
        (1, 1, 1),
        (2, 2, 0),
    ])
    def test_different_processes_dont_pick_up_each_others_requests(self, max_batch_size, req_count_1, req_count_2):
        """
        This is a test for horizontal scaling functionality of the Configuration Controller.
        It tests if two processes (in this case associated with different Session instances) only pick those requests
        that have no lock on them.
        """
        # Given
        config = self.get_config()
        config.MAX_REQUEST_BATCH_SIZE = max_batch_size
        session1 = Session(bind=self.engine)
        session2 = Session(bind=self.engine)

        consumer = RequestDBConsumer("someRequest", request_max_batch_size=config.MAX_REQUEST_BATCH_SIZE)
        self._prepare_two_pending_and_one_processed_request()

        # When
        reqs1 = consumer.get_pending_requests(session1)
        reqs2 = consumer.get_pending_requests(session2)

        reqs1_list = list(reqs1.values())[0]
        reqs2_list = list(reqs2.values())[0]

        session1.commit()
        session2.commit()

        # Then
        self.assertEqual(req_count_1, len(reqs1_list))
        self.assertEqual(req_count_2, len(reqs2_list))
        if reqs1_list and reqs2_list:
            # Making sure we're not getting the same requests in both sessions
            self.assertNotEqual(reqs1_list[0].cbsd_id, reqs2_list[0].cbsd_id)

        session1.close()
        session2.close()

    def _prepare_two_pending_and_one_processed_request(self):
        req_type = DBRequestType(name="someRequest")
        pending_status = DBRequestState(name="pending")
        processed_status = DBRequestState(name="processed")
        req1 = DBRequest(cbsd_id="foo1", type=req_type, state=pending_status, payload={"some": "payload1"})
        req2 = DBRequest(cbsd_id="foo2", type=req_type, state=pending_status, payload={"some": "payload2"})
        req3 = DBRequest(cbsd_id="foo3", type=req_type, state=processed_status, payload={"some": "payload3"})
        self.session.add_all([req1, req2, req3])
        self.session.commit()
