import json
import logging

import requests
import yaml
from requests import Response

from configuration_controller.request_router.exceptions import RequestRouterException


class RequestRouter:
    """
    This class is responsible for sending requests to SAS and forwarding SAS responses to Radio Controller.
    """

    def __init__(self,
                 sas_url: str,
                 rc_ingest_url: str,
                 cert_path: str,
                 ssl_key_path: str,
                 request_mapping_file_path: str):
        self.sas_url = sas_url
        self.rc_ingest_url = rc_ingest_url
        self.cert_path = cert_path
        self.ssl_key_path = ssl_key_path
        self.post_headers = {'Content-Type': 'application/json'}
        with open(request_mapping_file_path) as f:
            self.request_mapping = yaml.load(f, Loader=yaml.SafeLoader)

    def post_to_sas(self, request_json: str) -> Response:
        """
        This method parses a JSON request and sends it to the appropriate SAS endpoint.
        It will only look at the first key of the parsed JSON dict, so if there are multiple request types chunked in
        one dictionary it will send them to a SAS endpoint pertaining to the first key of the dictionary only.
        Therefore it is important to pass the requests grouped under one request name
        :param request_json: JSON object with a name as key and an array of objects as value
        :return: Response object with SAS response as json payload
        """
        request_dict = json.loads(request_json)
        request_name = next(iter(request_dict))
        try:
            sas_method = self.request_mapping[request_name]
        except KeyError:
            err_msg = f'Unable to find SAS method matching {request_name}'
            logging.error(err_msg)
            raise RequestRouterException(err_msg)
        sas_response = requests.post(
            f'{self.sas_url}/{sas_method}',
            json=request_json,
            cert=(self.cert_path, self.ssl_key_path),
            headers=self.post_headers,
        )
        return sas_response

    def redirect_sas_response_to_radio_controller(self, response: Response):
        """
        The method takes the Response object and passes its payload on to Radio Controller's ingest endpoint
        :param response: Response object
        :return: Response object
        """
        payload = response.json()
        return requests.post(self.rc_ingest_url, json=payload, headers=self.post_headers)
