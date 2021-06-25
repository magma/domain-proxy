import logging

from sqlalchemy import func

from configuration_controller.custom_types.custom_types import RequestsMap
from db_service.models import DBRequest, DBRequestState, DBRequestType
from mappings.types import RequestStates

logger = logging.getLogger(__name__)


class RequestDBConsumer:
    """Class to consume requests from the db"""

    def __init__(self, request_type: str, request_max_batch_size: int):
        self.request_type = request_type
        self.request_max_batch_size = request_max_batch_size

    def get_pending_requests(self, session) -> RequestsMap:
        db_requests = session.query(DBRequest) \
            .join(DBRequestType, DBRequestState) \
            .filter(DBRequestType.name == self.request_type,
                    DBRequestState.name == RequestStates.PENDING.value,
                    func.pg_try_advisory_xact_lock(DBRequest.id)) \
            .limit(self.request_max_batch_size)

        db_requests_num = db_requests.count()

        if db_requests_num:
            logger.info(f"[{self.request_type}] Fetched {db_requests_num} pending <{self.request_type}> requests.")

        return {self.request_type: db_requests.all()}
