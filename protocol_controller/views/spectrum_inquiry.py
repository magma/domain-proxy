import logging

from flask import Blueprint, Response

spectrum_inquiry_page = Blueprint("spectrumInquiry", __name__)


@spectrum_inquiry_page.route('/spectrumInquiry', methods=('POST', ))
def registration():
    logging.info('Executed spectrumInquiry action')
    return Response(status=200)
