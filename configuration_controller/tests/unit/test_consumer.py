import unittest
import mock
import json

from configuration_controller.consumer.consumer import RequestsConsumer


class TestConsumerNoHostException(unittest.TestCase):
    def test_exception_raise(self):
        self.assertRaises(Exception, lambda: RequestsConsumer())


class TestConsumerProcessDataEvents(unittest.TestCase):

    @staticmethod
    def _mock_on_message_call(consumer):
        requests = [
            {'routing_key': 'registrationRequest',
             'body': '{"object_number": 1}'},
            {'routing_key': 'deregistrationRequest',
             'body': '{"object_number": 2}'},
            {'routing_key': 'registrationRequest',
             'body': '{"object_number": 3}'},
        ]
        for request in requests:
            consumer._queue_callback(request['routing_key'], request['body'])

    @mock.patch('pika.BlockingConnection')
    def test_process_data_events_empty(self, mock_BlockingConnection):
        consumer = RequestsConsumer('1.1.1.1')
        self.assertIsInstance(consumer.process_data_events(), dict)

    @mock.patch('pika.BlockingConnection')
    def test_process_data_events_non_empty(self, mock_BlockingConnection):
        consumer = RequestsConsumer('1.1.1.1')
        consumer._channel.connection.process_data_events = mock.Mock(
            side_effect=lambda time_limit:
                self._mock_on_message_call(consumer))
        received_requests = consumer.process_data_events()
        for request_key, requests_body in received_requests.items():
            collected_object_numbers = []
            for request_object in requests_body:
                collected_object_numbers.append(
                    json.loads(request_object)['object_number'])
            if request_key == 'registrationRequest':
                self.assertEqual(len(requests_body), 2)
                self.assertListEqual(collected_object_numbers, [1, 3])
            elif request_key == 'deregistrationRequest':
                self.assertEqual(len(requests_body), 1)
                self.assertListEqual(collected_object_numbers, [2])
            else:
                self.assertEqual(len(requests_body), 0)
                self.assertListEqual(collected_object_numbers, [])
