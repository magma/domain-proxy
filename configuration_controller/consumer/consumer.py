import logging


logger = logging.getLogger(__name__)


class RequestsConsumer:
    """Class to consume requests from the db, needs implementing"""

    request_list = [
        "registrationRequest",
        "spectrumInquiryRequest",
        "grantRequest",
        "heartbeatRequest",
        "relinquishmentRequest",
        "deregistrationRequest",
    ]

    def __init__(self):
        pass

    def process_db_requests(self) -> dict:
        return {}
