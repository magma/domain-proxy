from configuration_controller.request_consumer.request_consumer import RequestConsumer
from configuration_controller.request_consumer.request_db_consumer import RequestDBConsumer
from db.db import DB


def request_consumer(db: DB, request_type: str) -> RequestConsumer:
    return RequestDBConsumer(db=db, request_type=request_type)
