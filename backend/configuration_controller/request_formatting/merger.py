import json
from collections import defaultdict
from json import JSONDecodeError

from configuration_controller.request_formatting.exceptions import PayloadFormatException


def merge_requests(requests_json: str) -> str:
    try:
        requests = json.loads(requests_json)
    except JSONDecodeError:
        raise PayloadFormatException('Requests not in a valid JSON format')

    merged_requests = defaultdict(list)

    for request in requests:
        for request_name, object_list in request.items():
            if merged_requests and request_name not in merged_requests:
                raise PayloadFormatException("Multiple request types detected")
            merged_requests[request_name].extend(object_list)
    return json.dumps(merged_requests)
