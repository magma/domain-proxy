from abc import ABC, abstractmethod

from configuration_controller.custom_types.custom_types import RequestsMap


class RequestConsumer(ABC):
    @abstractmethod
    def get_pending_requests(self) -> RequestsMap:
        pass
