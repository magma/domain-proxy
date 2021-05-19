import enum


class RequestTypes(enum.Enum):
    REGISTRATION = "registrationRequest"
    SPECTRUM_INQUIRY = "spectrumInquiryRequest"
    GRANT = "grantRequest"
    HEARTBEAT = "heartbeatRequest"
    RELINQUISHMENT = "relinquishmentRequest"
    DEREGISTRATION = "deregistrationRequest"


class RequestStates(enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
