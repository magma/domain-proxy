import unittest
import mock


from configuration_controller.consumer.consumer import RequestsConsumer


class TestConsumerNoHostException(unittest.TestCase):
    def test_exception_raise(self):
        self.assertRaises(Exception, lambda: RequestsConsumer())


class TestConsumerProcessDataEvents(unittest.TestCase):
    @mock.patch('pika.BlockingConnection')
    def test_process_data_events_empty(self, mock_BlockingConnection):
        consumer = RequestsConsumer('1.1.1.1')
        self.assertIsInstance(consumer.process_data_events(), dict)
