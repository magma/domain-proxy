import logging

from flask import Blueprint, Response

deregistration_page = Blueprint("deregistration", __name__)


@deregistration_page.route('/deregistration', methods=('POST', ))
def registration():
    logging.info('Executed deregistration action')
    return Response(status=200)
