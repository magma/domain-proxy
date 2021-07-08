from concurrent.futures import ThreadPoolExecutor

from parameterized import parameterized

from protocol_controller.plugins.cbsd_sas.tests.app_testcase import AppTestCase
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.deregistration_requests import \
    deregistration_requests
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.grant_requests import grant_requests
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.heartbeat_requests import heartbeat_requests
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.registration_requests import \
    registration_requests
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.relinquishment_requests import \
    relinquishment_requests
from protocol_controller.plugins.cbsd_sas.tests.fixtures.fake_requests.spectrum_inquiry_requests import \
    spectrum_inquiry_requests

incorrect_request_payload = {"incorrect": ["payload"]}


class RequestRoutingTestCase(AppTestCase):

    @parameterized.expand([
        ('registration', registration_requests[0], 1),
        ('registration', registration_requests[1], 2),
        ('deregistration', deregistration_requests[0], 1),
        ('relinquishment', relinquishment_requests[0], 1),
        ('grant', grant_requests[0], 1),
        ('heartbeat', heartbeat_requests[0], 1),
        ('spectrumInquiry', spectrum_inquiry_requests[0], 1),
    ])
    def test_cbsd_gets_response_from_sas(self, route, request_payload, expected_resp_len):
        # Given / When
        resp = self.client.post(
            f'/sas/v1/{route}',
            follow_redirects=True,
            json=request_payload
        )

        # Then
        self.assertEqual(expected_resp_len, len(resp.json[f"{route}Response"]))

    @parameterized.expand([
        ('registration', incorrect_request_payload),
        ('deregistration', incorrect_request_payload),
        ('relinquishment', incorrect_request_payload),
        ('grant', incorrect_request_payload),
        ('heartbeat', incorrect_request_payload),
        ('spectrumInquiry', incorrect_request_payload),
    ])
    def test_dp_raises_400_when_payload_doent_pass_validation(self, route, payload):
        # Given / When
        resp = self.client.post(
            f'/sas/v1/{route}',
            follow_redirects=True,
            json=payload
        )

        # Then
        self.assertEqual(400, resp.status_code)

    def test_cbsd_only_gets_response_from_sas_for_the_request_it_sent(self):
        # Given / When
        response_name = "registrationResponse"
        with ThreadPoolExecutor() as executor:
            resps = executor.map(lambda payload:
                                 self.client.post(f'/sas/v1/registration', follow_redirects=True, json=payload),
                                 registration_requests)

        resps = list(resps)
        resps.sort(key=lambda resp: len(resp.json[response_name]))

        # Then
        self.assertEqual(2, len(resps))
        self.assertEqual(1, len(resps[0].json[response_name]))
        self.assertEqual(2, len(resps[1].json[response_name]))
