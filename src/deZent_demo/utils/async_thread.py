import sys
import threading
from queue import Queue
import asyncio
from abc import ABC, abstractmethod
from typing import cast, Any, TypeVar, Generic, ClassVar, override
from collections.abc import Coroutine

CoroutineReturnT = TypeVar("CoroutineReturnT")
CoroutineT = Coroutine[Any, Any, CoroutineReturnT]
class AsyncThread(ABC):

    def __init__(self, auto_start: bool) -> None:
        self.event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()

        self.main_task: asyncio.Task[Any] | None = None

        self.thread = threading.Thread(
            target=self.__thread_runner__
        )
        if auto_start:
            self.start()

    def start(self) -> None:
        self.thread.start()
        self._loop_ready.wait() # wait until loop alive

    def stop(self) -> None:
        print("Stopping AsyncThread...")
        if self.main_task is not None:
            self.event_loop.call_soon_threadsafe(self.main_task.cancel)
        print("Stopping AsyncThread Eventloop...")
        self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        print("Waiting for thread...")
        self.thread.join()
        print("Stopped AsyncThread.")

    def dispatch_sync(self, coroutine: CoroutineT[CoroutineReturnT], timeout_s: float | None = None) -> CoroutineReturnT:
        return cast(CoroutineReturnT, self.__dispatch__(coroutine, timeout_s))
    
    def dispatch_async(self, coroutine: CoroutineT[CoroutineReturnT]) -> None:
        self.__dispatch__(coroutine, -1)

    def __dispatch__(self, coroutine: CoroutineT[CoroutineReturnT], timeout_s: float | None) -> CoroutineReturnT | None:
        self._loop_ready.wait() # wait until loop alive

        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.event_loop
        )
        if not timeout_s or not timeout_s < 0: # wait forever or timeout
            return future.result(timeout_s)
        else: # negative time out -> dispatch async, dont wait for return
            del future
            return None

    def __thread_runner__(self) -> None:
        asyncio.set_event_loop(self.event_loop)
        self.main_task = self.event_loop.create_task(self.__run__())
        self._loop_ready.set() # mark loop alive
        self.event_loop.run_until_complete(self.main_task)

    @abstractmethod
    async def __run__(self) -> None:
        pass


class RepeatingWorkerThread(ABC):

    def __init__(self,
                 start_immediately: bool = True):
        self.__exception: BaseException | None = None

        self.__start_event = threading.Event() # set when start is called
        self.__started_event = threading.Event() # set when the thread actually started
        self.__stop_event = threading.Event() # set when stop is called
        self.__stopped_event = threading.Event() # set when the thread actually stopped

        self.__thread = threading.Thread(
            target=self.__run,
        )

        if start_immediately:
            self.start()

    def start(self) -> bool:
        if not self._initiate_start():
            return False
        self._wait_started()
        return True
        
    def stop(self) -> bool:
        if not self._initiate_stop():
            return False
        if self.__on_this_thread():
            # allow killing self, without obligation
            # calling stop on oneself can only happen in _repeat
            # print for the user, and mark stop successful
            print(f"{type(self).__name__} stopped its own thread!", file=sys.stderr, flush=True)
            return True
        self._wait_stopped()
        self.__raise_exception()
        return True

    def __run(self) -> None:
        self.__started_event.set()
        try:
            while not self.__stop_event.is_set():
                self._repeat()
        except BaseException as e:
            self.__exception = e
        finally: 
            self.__stopped_event.set()

    @abstractmethod
    def _repeat(self) -> None:
        pass

    def _initiate_start(self) -> bool:
        if self.__start_event.is_set(): # start was called alr
            return False
        self.__start_event.set() # set start was called
        self.__thread.start() # start the thread
        return True

    def _wait_started(self) -> None:
        self.__started_event.wait()

    def _initiate_stop(self) -> bool:
        if self.__stop_event.is_set(): # stop was called alr
            return False
        # this stops the worker loop
        self.__stop_event.set() # set stop was called
        return True

    def _wait_stopped(self) -> None:
        self.__stopped_event.wait() # redundant
        self.__thread.join() # will always wait until Thread ended

    def __on_this_thread(self) -> bool:
        return threading.current_thread() is self.__thread

    def __raise_exception(self) -> None:
        if self.__exception is not None:
            raise self.__exception

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
