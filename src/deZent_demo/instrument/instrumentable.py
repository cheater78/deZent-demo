from abc import ABC
from typing import Generic, TypeVar

from .instrumentor import Instrumentor

InstrumentorType = TypeVar("InstrumentorType")
class Instrumentable(ABC, Generic[InstrumentorType]):

    def __init__(self,
                 instrumentor: InstrumentorType | None = None) -> None:
        super().__init__()

        self.instrumentor: InstrumentorType | None = instrumentor

    def instrument_trigger(self) -> None:
        pass