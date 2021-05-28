from parameterized import parameterized

from protocol_controller.tests.app_testcase import AppTestCase


class RequestRoutingTestCase(AppTestCase):

    @parameterized.expand([
        ('registration',),
        ('deregistration',),
        ('relinquishment',),
        ('grant',),
        ('heartbeat',),
        ('spectrumInquiry',),
    ])
    def test_protocol_controller_gets_response_from_radio_controller(self, route):
        # Given

        # When
        resp = self.client.post(
            f'/sas/v1/{route}',
            follow_redirects=True,
            json={f"{route}Request": [{"some": "payload"}]}
        )

        # Then
        self.assertEqual(1, len(resp.json[f"{route}Response"]))
