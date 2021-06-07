import logging

from db.db import DB
from configuration_controller.custom_types.custom_types import RequestsMap
from configuration_controller.request_consumer.request_consumer import RequestConsumer
from db.types import RequestStates

logger = logging.getLogger(__name__)


class RequestDBConsumer(RequestConsumer):
    """Class to consume requests from the db, needs implementing"""

    def __init__(self, db: DB, request_type: str):
        self.db = db
        self.request_type = request_type

    def get_pending_requests(self) -> RequestsMap:
        db_requests = self.db.get_requests(
            self.request_type, RequestStates.PENDING.value)
        if db_requests:
            logger.info(f"[{self.request_type}] Fetched {len(db_requests)} pending <{self.request_type}> requests.")
        return {self.request_type: db_requests}
