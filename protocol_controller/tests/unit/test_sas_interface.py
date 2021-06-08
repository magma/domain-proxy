from unittest.mock import patch

from parameterized import parameterized

from protocol_controller.tests.app_testcase import AppTestCase

REGISTRATION = 'registration'
DEREGISTRATION = 'deregistration'
RELINQUISHMENT = 'relinquishment'
GRANT = 'grant'
HEARTBEAT = 'heartbeat'
SPECTRUM_INQUIRY = 'spectrumInquiry'
POST = 'post'
GET = 'get'
PUT = 'put'
PATCH = 'patch'
DELETE = 'delete'


class SASProtocolControllerTests(AppTestCase):

    @parameterized.expand([
        (REGISTRATION, POST, 200),
        (REGISTRATION, GET, 405),
        (REGISTRATION, PUT, 405),
        (REGISTRATION, PATCH, 405),
        (REGISTRATION, DELETE, 405),
        (DEREGISTRATION, POST, 200),
        (DEREGISTRATION, GET, 405),
        (DEREGISTRATION, PUT, 405),
        (DEREGISTRATION, PATCH, 405),
        (DEREGISTRATION, DELETE, 405),
        (RELINQUISHMENT, POST, 200),
        (RELINQUISHMENT, GET, 405),
        (RELINQUISHMENT, PUT, 405),
        (RELINQUISHMENT, PATCH, 405),
        (RELINQUISHMENT, DELETE, 405),
        (GRANT, POST, 200),
        (GRANT, GET, 405),
        (GRANT, PUT, 405),
        (GRANT, PATCH, 405),
        (GRANT, DELETE, 405),
        (HEARTBEAT, POST, 200),
        (HEARTBEAT, GET, 405),
        (HEARTBEAT, PUT, 405),
        (HEARTBEAT, PATCH, 405),
        (HEARTBEAT, DELETE, 405),
        (SPECTRUM_INQUIRY, POST, 200),
        (SPECTRUM_INQUIRY, GET, 405),
        (SPECTRUM_INQUIRY, PUT, 405),
        (SPECTRUM_INQUIRY, PATCH, 405),
        (SPECTRUM_INQUIRY, DELETE, 405),
    ])
    def test_route_response_200_for_post_and_405_for_other_methods(self, route, method, expected_status):
        # Given
        with patch(f'protocol_controller.grpc_communication.get_common_rc_response.upload_requests') as mockupload:
            mockupload.return_value.msg = ['{"any": "response"}']

            # When
            req_method = getattr(self.client, method)
            response = req_method(f'/sas/v1/{route}')

            # Then
            self.assertEqual(response.status_code, expected_status)
