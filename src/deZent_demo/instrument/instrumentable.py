from abc import ABC
from typing import Any

from .instrumentor import Instrumentor, InstrumentEvent

class Instrumentable(ABC):

    def __init__(
        self,
        instrumentor: Instrumentor,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.__instrumentor: Instrumentor = instrumentor

    def set_instrumentor(self, instrumentor: Instrumentor) -> None:
        self.__instrumentor = instrumentor

    def _instrument(self, event: InstrumentEvent, *args: Any) -> None:
        self.__instrumentor.call(event, *args)