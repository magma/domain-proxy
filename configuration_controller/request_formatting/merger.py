import json
from collections import defaultdict
from typing import List


def merge_requests(requests_list: List[str]) -> str:
    """
    This function receives an array of JSON objects and merges them into one JSON object with request names as keys and
    sub-arrays of objects as values

    example:

    '[{"foo": [{...}]}, {"foo": [{...}]}]' will be serialized to '[{"foo": [{...}, {...}]}]'

    :param requests_list: List of requests in the following format '[{"foo": [{...}]}, ...]'
    :return: JSON serialized object with a subarray of payloads
    """

    merged_requests = defaultdict(list)

    for request in requests_list:
        request = json.loads(request)
        for request_name, payload in request.items():
            merged_requests[request_name].extend(payload)

    return json.dumps(merged_requests)
