import logging
from abc import ABC, abstractmethod
from typing import List

from requests import Response

from db.models import DBRequest

logger = logging.getLogger(__name__)


class ResponseProcessor(ABC):
    @abstractmethod
    def process_response(self, requests: List[DBRequest], response: Response) -> None:
        pass
