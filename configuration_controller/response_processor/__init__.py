from configuration_controller.response_processor.response_processor import ResponseProcessor
from configuration_controller.response_processor.response_db_processor import (
    DeregistrationResponseDBProcessor,
    GrantResponseDBProcessor,
    HeartbeatResponseDBProcessor,
    RegistrationResponseDBProcessor,
    RelinquishmentResponseDBProcessor,
    SpectrumInquiryDBProcessor)
from db.db import DB


_processors = {
    "registrationRequest": RegistrationResponseDBProcessor,
    "spectrumInquiryRequest": SpectrumInquiryDBProcessor,
    "grantRequest": GrantResponseDBProcessor,
    "heartbeatRequest": HeartbeatResponseDBProcessor,
    "relinquishmentRequest": RelinquishmentResponseDBProcessor,
    "deregistrationRequest": DeregistrationResponseDBProcessor,
}


def response_processor(db: DB, request_type: str) -> ResponseProcessor:
    cls = _processors[request_type]
    return cls(db)
