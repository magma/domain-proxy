from configuration_controller.response_processor.strategies.map_keys_generation import (
    generate_compound_request_map_key,
    generate_compound_response_map_key,
    generate_registration_request_map_key,
    generate_simple_request_map_key,
    generate_simple_response_map_key,
)
from configuration_controller.response_processor.strategies.response_processing import (
    process_deregistration_responses,
    process_grant_responses,
    process_heartbeat_responses,
    process_registration_responses,
    process_relinquishment_responses,
    process_spectrum_inquiry_responses,
)

processor_strategies = {
    "registrationRequest": {
        "request_map_key": generate_registration_request_map_key,
        "response_map_key": generate_simple_response_map_key,
        "process_responses": process_registration_responses,
    },
    "spectrumInquiryRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
        "process_responses": process_spectrum_inquiry_responses,
    },
    "grantRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
        "process_responses": process_grant_responses,
    },
    "heartbeatRequest": {
        "request_map_key": generate_compound_request_map_key,
        "response_map_key": generate_compound_response_map_key,
        "process_responses": process_heartbeat_responses,
    },
    "relinquishmentRequest": {
        "request_map_key": generate_compound_request_map_key,
        "response_map_key": generate_compound_response_map_key,
        "process_responses": process_relinquishment_responses,
    },
    "deregistrationRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
        "process_responses": process_deregistration_responses,
    },
}
