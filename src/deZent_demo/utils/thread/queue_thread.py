from queue import Queue
from abc import abstractmethod
from typing import TypeVar, Generic, ClassVar, override

from .repeating_thread import RepeatingWorkerThread


QueueElementType = TypeVar("QueueElementType")
class QueueWorkerThreadStopSentinel:
    pass

class QueueWorkerThread(RepeatingWorkerThread, Generic[QueueElementType]):
    __stop_sentinel: ClassVar[QueueWorkerThreadStopSentinel] = QueueWorkerThreadStopSentinel() # unique stop sentinel

    def __init__(self,
                 start_immediately: bool = True):
        self._queue: Queue[QueueElementType | QueueWorkerThreadStopSentinel] = Queue()

        super().__init__(start_immediately)
    
    def dispatch(self, element: QueueElementType) -> None:
        self._queue.put(element)

    def dispatch_nowait(self, element: QueueElementType) -> None:
        self._queue.put_nowait(element)

    @override
    def _repeat(self) -> None:
        element: QueueElementType | QueueWorkerThreadStopSentinel = self._queue.get()
        # exit / recheck the loop condition when receiving the stop sentinel
        # since we have a dedicated type a type match is sufficient
        if isinstance(element, QueueWorkerThreadStopSentinel) \
            or element == self.__stop_sentinel:
            return
        self._handle_element(element)

    @abstractmethod
    def _handle_element(self, element: QueueElementType) -> None:
        pass
    
    @override
    def _initiate_stop(self) -> bool:
        if not super()._initiate_stop():
            return False
        self.__put_stop_sentinel() # frees the queue get wait block
        return True

    def __put_stop_sentinel(self) -> None:
        self._queue.put(self.__stop_sentinel)