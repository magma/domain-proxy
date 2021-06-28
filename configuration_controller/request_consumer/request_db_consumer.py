import logging

from sqlalchemy import func

from configuration_controller.custom_types.custom_types import RequestsMap
from db_service.models import DBRequest, DBRequestState, DBRequestType
from mappings.types import RequestStates

logger = logging.getLogger(__name__)


class RequestDBConsumer:
    """Class to consume requests from the db"""

    def __init__(self, request_type: str, request_processing_limit: int):
        self.request_type = request_type
        self.request_processing_limit = request_processing_limit

    def get_pending_requests(self, session) -> RequestsMap:
        """
        Getting requests in pending state and acquiring lock on them if they weren't previously locked
        by another process. If they have a lock on them, select the ones that don't.
        """
        db_requests_query = session.query(DBRequest) \
            .join(DBRequestType, DBRequestState) \
            .filter(DBRequestType.name == self.request_type,
                    DBRequestState.name == RequestStates.PENDING.value,
                    func.pg_try_advisory_xact_lock(DBRequest.id))

        if self.request_processing_limit > 0:
            db_requests_query = db_requests_query.limit(self.request_processing_limit)

        db_requests_num = db_requests_query.count()

        if db_requests_num:
            logger.info(f"[{self.request_type}] Fetched {db_requests_num} pending <{self.request_type}> requests.")

        return {self.request_type: db_requests_query.all()}
