from unittest import TestCase

from parameterized import parameterized

from configuration_controller.request_formatting.merger import merge_requests
from configuration_controller.tests.fixtures.fake_request_queues.registration_requests import registration_requests
from configuration_controller.tests.fixtures.fake_request_queues.mixed_queued_requests \
    import queued_requests as mixed_queued_requests
from configuration_controller.tests.fixtures.fake_request_queues.registration_requests_with_one_cumulative_request \
    import registration_requests_with_cumulative


class RequestMergingTestCase(TestCase):

    def test_request_merging_returns_empty_dict_for_empty_request_list(self):
        # Given / When
        merged_requests = merge_requests([])

        # Then
        self.assertEqual({}, merged_requests)

    @parameterized.expand([
        (registration_requests, 1, 2),
        (registration_requests_with_cumulative, 1, 3),
    ])
    def test_request_merging_merges_multiple_requests_into_one(self, _requests, nr_of_keys, nr_of_elems_in_list):
        # Given / When
        merged_requests = merge_requests(_requests)

        # Then
        self.assertIsInstance(merged_requests, dict)
        self.assertEqual(nr_of_keys, len(merged_requests.keys()))
        self.assertIsInstance(list(merged_requests.values())[0], list)
        self.assertEqual(nr_of_elems_in_list, len(list(merged_requests.values())[0]))

    def test_request_merging_merges_mixed_type_of_requests_into_one(self):
        # Given / When
        merged_requests = merge_requests(mixed_queued_requests)

        # Then
        self.assertEqual(2, len(merged_requests.keys()))
        self.assertEqual(2, len(merged_requests.values()))
        self.assertEqual(1, len(list(merged_requests.values())[0]))
        self.assertEqual(1, len(list(merged_requests.values())[1]))
