from configuration_controller.response_processor.strategies.map_keys_generation import generate_simple_response_map_key, \
    generate_compound_response_map_key

processor_strategies = {
    "registrationRequest": {
        "response_map_key": generate_simple_response_map_key,
    },
    "spectrumInquiryRequest": {
        "response_map_key": generate_simple_response_map_key,
    },
    "grantRequest": {
        "response_map_key": generate_simple_response_map_key,
    },
    "heartbeatRequest": {
        "response_map_key": generate_compound_response_map_key,
    },
    "relinquishmentRequest": {
        "response_map_key": generate_simple_response_map_key,
    },
    "deregistrationRequest": {
        "response_map_key": generate_simple_response_map_key,
    },
}
