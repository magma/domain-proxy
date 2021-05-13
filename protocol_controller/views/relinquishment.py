import logging

from flask import Blueprint, Response

relinquishment_page = Blueprint("relinquishment", __name__)


@relinquishment_page.route('/relinquishment', methods=('POST', ))
def registration():
    logging.info('Executed relinquishment action')
    return Response(status=200)
