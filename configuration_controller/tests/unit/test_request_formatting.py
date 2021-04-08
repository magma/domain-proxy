import json
from unittest import TestCase

from parameterized import parameterized

from configuration_controller.request_formatting.merger import PayloadFormatException, merge_requests


class RequestMergingTestCase(TestCase):

    def test_request_merging_returns_empty_json_obj_for_empty_request(self):
        # Given / When
        merged_requests = merge_requests('[]')

        # Then
        self.assertEqual('{}', merged_requests)

    @parameterized.expand([
        ('queued_requests.json', 1, 2),
        ('queued_requests_with_one_cumulative_request.json', 1, 3),
    ])
    def test_request_merging_merges_multiple_json_requests_into_one(self, fixture_file, nr_of_keys, nr_of_values):
        # Given
        json_requests = self._get_json_from_fixture(fixture_file)

        # When
        merged_requests = merge_requests(json_requests)
        deserialized_merged_requests = json.loads(merged_requests)

        # Then
        self.assertIsInstance(deserialized_merged_requests, dict)
        self.assertEqual(nr_of_keys, len(deserialized_merged_requests.keys()))
        self.assertIsInstance(list(deserialized_merged_requests.values())[0], list)
        self.assertEqual(nr_of_values, len(list(deserialized_merged_requests.values())[0]))

    def test_request_merging_raises_exception_for_mixed_requests_in_one_queue(self):
        # Given
        json_requests = self._get_json_from_fixture('mixed_queued_requests.json')

        # When / Then
        with self.assertRaises(PayloadFormatException):
            merge_requests(json_requests)

    def test_request_merging_raises_exception_for_wrong_request_structure(self):
        # Given

        # When / Then
        with self.assertRaises(PayloadFormatException):
            merge_requests('foo')

    @staticmethod
    def _get_json_from_fixture(fixture_name):
        with open(f'fixtures/fake_request_queues/{fixture_name}') as f:
            return json.dumps(json.load(f))
