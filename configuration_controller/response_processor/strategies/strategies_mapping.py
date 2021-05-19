from configuration_controller.response_processor.strategies.map_keys_generation import (
    generate_registration_request_map_key,
    generate_simple_request_map_key,
    generate_compound_request_map_key,
    generate_simple_response_map_key,
    generate_compound_response_map_key)

processor_strategies = {
    "registrationRequest": {
        "request_map_key": generate_registration_request_map_key,
        "response_map_key": generate_simple_response_map_key,
    },
    "spectrumInquiryRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
    },
    "grantRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
    },
    "heartbeatRequest": {
        "request_map_key": generate_compound_request_map_key,
        "response_map_key": generate_compound_response_map_key,
    },
    "relinquishmentRequest": {
        "request_map_key": generate_compound_request_map_key,
        "response_map_key": generate_compound_response_map_key,
    },
    "deregistrationRequest": {
        "request_map_key": generate_simple_request_map_key,
        "response_map_key": generate_simple_response_map_key,
    },
}
