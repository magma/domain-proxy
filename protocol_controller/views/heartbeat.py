import logging

from flask import Blueprint, Response

heartbeat_page = Blueprint("heartbeat", __name__)


@heartbeat_page.route('/heartbeat', methods=('POST', ))
def registration():
    logging.info('Executed heartbeat action')
    return Response(status=200)
