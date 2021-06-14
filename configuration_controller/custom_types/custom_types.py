from typing import Dict, List

from db_service.models import DBRequest

MergedRequests = Dict[str, List[Dict]]
RequestsMap = Dict[str, List[DBRequest]]
