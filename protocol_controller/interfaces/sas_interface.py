from flask import Flask
import protocol_controller.requests_handling.handler as requestHandler


class SASProtocolController:

    def __init__(self, name, version, port=8080, host='0.0.0.0'):
        self.server = Flask(name)
        self._version = version
        self._port = port
        self._host = host

    def run(self):
        self.server.run(host=self._host, port=self._port)

    def _add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.server.add_url_rule(endpoint, endpoint_name, handler)

    def add_sas_endpoints(self):
        self._add_endpoint(endpoint=f'/{self._version}/registration',
                           endpoint_name='registration',
                           handler=requestHandler.registration)
        self._add_endpoint(endpoint=f'/{self._version}/spectrumInquiry',
                           endpoint_name='spectrumInquiry',
                           handler=requestHandler.spectrumInquiry)
        self._add_endpoint(endpoint=f'/{self._version}/grant',
                           endpoint_name='grant',
                           handler=requestHandler.grant)
        self._add_endpoint(endpoint=f'/{self._version}/heartbeat',
                           endpoint_name='heartbeat',
                           handler=requestHandler.heartbeat)
        self._add_endpoint(endpoint=f'/{self._version}/relinquishment',
                           endpoint_name='relinquishment',
                           handler=requestHandler.relinquishment)
        self._add_endpoint(endpoint=f'/{self._version}/deregistration',
                           endpoint_name='deregistration',
                           handler=requestHandler.deregistration)
