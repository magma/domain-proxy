from parameterized import parameterized
from protocol_controller.tests.app_testcase import AppTestCase


class RequestRoutingTestCase(AppTestCase):

    @parameterized.expand([
        'registration',
        'deregistration',
        'relinquishment',
        'grant',
        'heartbeat',
        'spectrumInquiry',
    ])
    def test_protocol_controller_gets_response_from_radio_controller(self, route):
        resp = self.client.post(f'/sas/v1/{route}', follow_redirects=True, json={"some": "payload"})

        self.assertEqual('{"some": "payload"}', resp.json)
