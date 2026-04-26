from abc import ABC, abstractmethod


class CollecteConsumer(ABC):
    @abstractmethod
    def consommer(self) -> None:
        pass
