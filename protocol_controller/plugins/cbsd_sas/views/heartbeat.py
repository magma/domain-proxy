from flask import Blueprint, request
from flask_json import as_json

from protocol_controller.grpc_communication.get_common_rc_response import get_common_bulk_rc_response
from protocol_controller.plugins.cbsd_sas.validators.heartbeat_request import HeartbeatRequestSchema

heartbeat_page = Blueprint("heartbeat", __name__)


@heartbeat_page.route('/heartbeat', methods=('POST', ))
@as_json
def heartbeat():
    return get_common_bulk_rc_response(request, "heartbeatResponse", HeartbeatRequestSchema)
