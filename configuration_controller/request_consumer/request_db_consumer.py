import logging

from sqlalchemy import and_

from configuration_controller.custom_types.custom_types import RequestsMap
from db.models import DBRequest, DBRequestState, DBRequestType
from db.types import RequestStates

logger = logging.getLogger(__name__)


class RequestDBConsumer:
    """Class to consume requests from the db"""

    def __init__(self, request_type: str):
        self.request_type = request_type

    def get_pending_requests(self, session) -> RequestsMap:
        db_requests = session.query(DBRequest).join(DBRequestType, DBRequestState).filter(
            and_(
                DBRequestType.name == self.request_type,
                DBRequestState.name == RequestStates.PENDING.value
            )
        ).all()

        if db_requests:
            logger.info(f"[{self.request_type}] Fetched {len(db_requests)} pending <{self.request_type}> requests.")

        return {self.request_type: db_requests}
