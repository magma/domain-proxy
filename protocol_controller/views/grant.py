from flask import Blueprint, current_app, request
from flask_json import as_json

from protocol_controller.common.upload_request import upload_request

grant_page = Blueprint("grant", __name__)


@grant_page.route('/grant', methods=('POST', ))
@as_json
def registration():
    client = current_app.extensions["GrpcClient"]
    grpc_response = upload_request(client, "grant", request.json)
    return grpc_response.msg, 200
