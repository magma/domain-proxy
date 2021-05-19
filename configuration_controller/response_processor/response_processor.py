from configuration_controller.custom_types.custom_types import Request
import logging

from abc import ABC, abstractmethod
from typing import List


logger = logging.getLogger(__name__)


class ResponseProcessor(ABC):
    @abstractmethod
    def process_response(self, requests: List[Request], response: str) -> None:
        pass
