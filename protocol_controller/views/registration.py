from flask import Blueprint, current_app, request
from flask_json import as_json

from protocol_controller.common.upload_request import upload_request

registration_page = Blueprint("registration", __name__)


@registration_page.route('/registration', methods=('POST', ))
@as_json
def registration():
    client = current_app.extensions["GrpcClient"]
    grpc_response = upload_request(client, "registration", request.json)
    return grpc_response.msg, 200
