import json
import logging

from db.db import DB
from db.types import request_states
from configuration_controller.custom_types.custom_types import Request, RequestsMap
from configuration_controller.request_consumer.request_consumer import RequestConsumer


logger = logging.getLogger(__name__)


class RequestDBConsumer(RequestConsumer):
    """Class to consume requests from the db, needs implementing"""

    def __init__(self, db: DB, request_type: str):
        self.db = db
        self.request_type = request_type
        self.pending_state = request_states[request_states.index("pending")]

    def get_requests(self) -> RequestsMap:
        db_requests = self.db.get_requests(
            self.request_type, self.pending_state)
        requests = [Request(id=req.id, cbsd_id=req.cbsd_id, payload=req.payload) for req in db_requests]
        if requests:
            logger.info(
                f"[{self.request_type}] Fetched {len(db_requests)} pending <{self.request_type}> requests.")
        return {self.request_type: requests}
