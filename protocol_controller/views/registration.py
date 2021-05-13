import logging

from flask import Blueprint, Response

registration_page = Blueprint("registration", __name__)


@registration_page.route('/registration', methods=('POST', ))
def registration():
    logging.info('Executed registration action')
    return Response(status=200)
