from parameterized import parameterized
import unittest

from protocol_controller.interfaces.sas_interface import SASProtocolController


class SASProtocolControllerTests(unittest.TestCase):

    def setUp(self):
        server = SASProtocolController('test_server', 'sas/v1')
        server.add_sas_endpoints()
        server.server.config["TESTING"] = True
        self.server = server.server.test_client()

    @parameterized.expand([
       'registration',
       'spectrumInquiry',
       'grant',
       'heartbeat',
       'relinquishment',
       'deregistration'
    ])
    def test_route_response(self, route):
        response = self.server.get(f'/sas/v1/{route}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
