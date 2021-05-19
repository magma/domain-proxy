from typing import Dict, List, NamedTuple


class Request(NamedTuple):
    id: int
    cbsd_id: str
    payload: Dict


MergedRequests = Dict[str, List[Dict]]
RequestsMap = Dict[str, List[Request]]
