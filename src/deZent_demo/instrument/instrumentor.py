from enum import Enum
from typing import Any, ClassVar
from collections.abc import Callable

class InstrumentEvent(Enum):
    pass
InstrumentEventCallback = Callable[..., None]

class Instrumentor():
    event_type: ClassVar[type[InstrumentEvent] | None] = None
    event_cb_signatures: ClassVar[dict[InstrumentEvent, list[type]]] = { }
    
    def __init__(self) -> None:
        super().__init__()
        self._instrument_callbacks: dict[InstrumentEvent, InstrumentEventCallback] = { }

    def set_instrument_callback(self, event: InstrumentEvent, callback: InstrumentEventCallback) -> None:
        self._instrument_callbacks[event] = callback
    
    def call(self, event: InstrumentEvent, *args: Any) -> None:
        # Callbacks are optional, exit early if none was provided
        callback: InstrumentEventCallback | None = self._instrument_callbacks.get(event)
        if callback is None:
            return
        
        cls: type[Instrumentor] | None = None
        for c in self.__class__.__mro__:
            if not issubclass(c, Instrumentor):
                continue
            if c is Instrumentor:
                break # reached the base class
            if c.event_type is not None and isinstance(event, c.event_type):
                cls = c # most derived Instrumentor handling event's type

        if cls is None:
            return # event's type was not supported by this class and its super classes
        
        cls_event_cb_signatures: dict[InstrumentEvent, list[type]] = cls.event_cb_signatures

        # validate callback function signature -> call only if all types match
        callback_signature: list[type] | None = cls_event_cb_signatures.get(event)
        if callback_signature is None:
            raise RuntimeError(f"Instrumentor class: {self.__class__.__name__} has no registered function signature for Event: {event}!")
        if len(callback_signature) != len(args):
            raise RuntimeError(f"Instrumentor callback function signature: {callback_signature} for Event: {event} did not match length of provided args: {args}!")
        for arg_i, (arg, cb_sig_arg_t) in enumerate(zip(args, callback_signature)):
            if type(arg) != cb_sig_arg_t:
                raise RuntimeError(f"Instrumentor callback function signature: {callback_signature} for Event: {event} did not of provided args: {args}!\n \
                    provided arg[{arg_i}] of type: {type(arg)} did not match expected type: {cb_sig_arg_t}!")
        
        # finally call
        return callback(*args)

from PySide6.QtCore import Qt, QObject, Signal, QThread, Slot

'''
    Instrumentor synchronization layer to run all instrumentor callbacks on Qt's main Thread
'''
class QtThreadSafeInstrumentor(QObject, Instrumentor):
    cb_signal = Signal(InstrumentEvent, object)

    def __init__(self) -> None:
        QObject.__init__(self)
        Instrumentor.__init__(self) # type: ignore

        self.cb_signal.connect(
            self._dispatch,
            Qt.ConnectionType.BlockingQueuedConnection,
        )

    def call(self, event: InstrumentEvent, *args: Any) -> None:
        if QThread.currentThread() == self.thread(): # signaling on the main Thread will deadlock!
            Instrumentor.call(self, event, *args) # type: ignore , so just call immediately
        else:
            self.cb_signal.emit(event, args)

    @Slot(InstrumentEvent, object) # type: ignore (InstrumentEvent, tuple[Any, ...])
    def _dispatch(self, event: InstrumentEvent, payload: tuple[Any, ...]) -> None:
        Instrumentor.call(self, event, *payload) # type: ignore