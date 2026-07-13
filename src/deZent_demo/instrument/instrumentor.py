from abc import ABC
from enum import Enum
from typing import Callable, Any, Generic, TypeVar


class InstrumentEvent(Enum):
    pass
InstrumentEventType = TypeVar("InstrumentEventType", bound=Enum)

InstrumentEventCallback = Callable[[Any], None] # TODO

class Instrumentor(ABC, Generic[InstrumentEventType]):

    def __init__(self) -> None:
        super().__init__()

        self.instrument_callbacks: dict[InstrumentEventType, InstrumentEventCallback] = { }

    def set_instrument_callback(self, event: InstrumentEventType, callback: InstrumentEventCallback) -> None:
        self.instrument_callbacks[event] = callback
    
    def call(self, event: InstrumentEventType, *args: Any, **kwargs: Any) -> None:
        callback: InstrumentEventCallback | None = self.instrument_callbacks.get(event)
        if callback is None:
            return
        return callback(*args, **kwargs)
    