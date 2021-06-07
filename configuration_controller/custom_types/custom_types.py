from typing import Dict, List

from db.models import DBRequest

MergedRequests = Dict[str, List[Dict]]
RequestsMap = Dict[str, List[DBRequest]]
