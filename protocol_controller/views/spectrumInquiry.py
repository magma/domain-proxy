from flask import Blueprint, current_app, request
from flask_json import as_json

from protocol_controller.common.upload_request import upload_request

spectrum_inquiry_page = Blueprint("spectrumInquiry", __name__)


@spectrum_inquiry_page.route('/spectrumInquiry', methods=('POST', ))
@as_json
def registration():
    client = current_app.extensions["GrpcClient"]
    grpc_response = upload_request(client, "spectrumInquiry", request.json)
    return grpc_response.msg, 200
