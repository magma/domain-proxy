import logging

from flask import Blueprint, Response

grant_page = Blueprint("grant", __name__)


@grant_page.route('/grant', methods=('POST', ))
def registration():
    logging.info('Executed grant action')
    return Response(status=200)
