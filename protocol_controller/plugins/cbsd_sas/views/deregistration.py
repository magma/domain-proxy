from flask import Blueprint, request
from flask_json import as_json

from protocol_controller.grpc_communication.get_common_rc_response import get_common_bulk_rc_response
from protocol_controller.plugins.cbsd_sas.validators.deregistration_request import DeregistrationRequestSchema

deregistration_page = Blueprint("deregistration", __name__)


@deregistration_page.route('/deregistration', methods=('POST', ))
@as_json
def deregistration():
    return get_common_bulk_rc_response(request, "deregistrationResponse", DeregistrationRequestSchema)
