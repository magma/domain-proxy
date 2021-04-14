import os
import unittest

import pika as pika
from parameterized import parameterized

from configuration_controller.consumer.consumer import RequestsConsumer
from configuration_controller.request_router.request_router import RequestRouter
from configuration_controller.run import get_config, process_requests
from configuration_controller.tests.fixtures.fake_request_queues.deregistration_requests import deregistration_requests
from configuration_controller.tests.fixtures.fake_request_queues.grant_requests import grant_requests
from configuration_controller.tests.fixtures.fake_request_queues.heartbeat_requests import heartbeat_requests
from configuration_controller.tests.fixtures.fake_request_queues.registration_requests import registration_requests
from configuration_controller.tests.fixtures.fake_request_queues.relinquishment_requests import relinquishment_requests
from configuration_controller.tests.fixtures.fake_request_queues.spectrum_inquiry_requests import \
    spectrum_inquiry_requests


class ConfigurationControllerTestCase(unittest.TestCase):
    requests_dict = {
        "registrationRequest": registration_requests,
        "deregistrationRequest": deregistration_requests,
        "spectrumInquiryRequest": spectrum_inquiry_requests,
        "grantRequest": grant_requests,
        "heartbeatRequest": heartbeat_requests,
        "relinquishmentRequest": relinquishment_requests,
    }

    def setUp(self) -> None:
        os.environ['APP_CONFIG'] = 'configuration_controller.config.TestConfig'
        self.config = get_config()
        self.consumer = RequestsConsumer(rabbitmq_url=self.config.RABBITMQ_HOST)
        self.router = RequestRouter(
            sas_url=self.config.SAS_URL,
            rc_ingest_url=self.config.RC_INGEST_URL,
            cert_path=self.config.CC_CERT_PATH,
            ssl_key_path=self.config.CC_SSL_KEY_PATH,
            request_mapping_file_path=self.config.REQUEST_MAPPING_FILE_PATH,
            ssl_verify=False,
        )

    def tearDown(self):
        super().tearDown()
        self.consumer._connection.close()

    def populate_queue(self, q_name):
        conn_params = pika.ConnectionParameters(self.config.RABBITMQ_HOST)
        connection = pika.BlockingConnection(conn_params)
        channel = connection.channel()
        channel.exchange_declare(exchange='requests', exchange_type='topic')

        for req in self.requests_dict[q_name]:
            channel.basic_publish(exchange='requests', routing_key=q_name, body=req)

        connection.close()

    @parameterized.expand([
        ("registrationRequest", "registrationResponse", 2),
        ("deregistrationRequest", "deregistrationResponse", 2),
        ("heartbeatRequest", "heartbeatResponse", 2),
        ("grantRequest", "grantResponse", 2),
        ("relinquishmentRequest", "relinquishmentResponse", 2),
        ("spectrumInquiryRequest", "spectrumInquiryResponse", 1),
    ])
    def test_requests_processed(self, queue_name, sas_response_obj, sas_response_array_len):
        # Given
        self.populate_queue(queue_name)

        # When
        sas_responses = process_requests(self.consumer, self.router)

        # Then
        self.assertEqual(sas_response_array_len, len(sas_responses[0].json()[sas_response_obj]))
