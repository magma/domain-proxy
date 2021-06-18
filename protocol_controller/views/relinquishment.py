from flask import Blueprint, request
from flask_json import as_json

from protocol_controller.grpc_communication.get_common_rc_response import get_common_bulk_rc_response
from protocol_controller.validators.relinquishment_request import RelinquishmentRequestSchema

relinquishment_page = Blueprint("relinquishment", __name__)


@relinquishment_page.route('/relinquishment', methods=('POST', ))
@as_json
def relinquishment():
    return get_common_bulk_rc_response(request, "relinquishmentResponse", RelinquishmentRequestSchema)
