import json
from collections import defaultdict
from json import JSONDecodeError

from configuration_controller.request_formatting.exceptions import PayloadFormatException


def merge_requests(requests_json: str) -> str:
    """
    This function receives an array of JSON objects and merges them into one json object with a subarray of objects as
    long as the keys of the objects are the same.
    If the keys differ, it will raise a PayloadFormatException

    example:

    '[{"foo": [{...}]}, {"foo": [{...}]}]' will be serialized to '[{"foo": [{...}, {...}]}]'
    but '[{"foo": [{...}]}, {"baz": [{...}]}]' will raise an exception.

    :param requests_json: JSON serialized array of requests in the following format '[{"foo": [{...}]}, ...]'
    :return: JSON serialized object with a subarray of payloads
    """
    try:
        requests = json.loads(requests_json)
    except JSONDecodeError:
        raise PayloadFormatException('Requests not in a valid JSON format')

    merged_requests = defaultdict(list)

    for request in requests:
        for request_name, object_list in request.items():
            if merged_requests and merged_requests.get(request_name) is None:
                raise PayloadFormatException("Multiple request types detected")
            merged_requests[request_name].extend(object_list)
    return json.dumps(merged_requests)
