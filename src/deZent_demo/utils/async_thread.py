import asyncio
import threading
from abc import ABC, abstractmethod
from typing import cast, Any, TypeVar
from collections.abc import Coroutine

CoroutineReturnT = TypeVar("CoroutineReturnT")
CoroutineT = Coroutine[Any, Any, CoroutineReturnT]
class AsyncThread(ABC):

    def __init__(self, auto_start: bool) -> None:
        self.event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.__thread_runner__,
            daemon=True
        )
        if auto_start:
            self.start()

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self.__shutdown_event_loop__(),
            self.event_loop,
        )
        future.result()

        self.event_loop.call_soon_threadsafe(
            self.event_loop.stop
        )
        self.thread.join()

    def dispatch_sync(self, coroutine: CoroutineT[CoroutineReturnT], timeout: float | None = None) -> CoroutineReturnT:
        return cast(CoroutineReturnT, self.__dispatch__(coroutine, timeout))
    
    def dispatch_async(self, coroutine: CoroutineT[CoroutineReturnT]) -> None:
        self.__dispatch__(coroutine, -1)

    def __dispatch__(self, coroutine: CoroutineT[CoroutineReturnT], timeout: float | None) -> CoroutineReturnT | None:
        future = asyncio.run_coroutine_threadsafe(
            coroutine,
            self.event_loop
        )
        if not timeout or not timeout < 0: # wait forever or timeout
            return future.result(timeout)
        else: # negative time out -> dispatch async, dont wait for return
            del future
            return None

    async def __shutdown_event_loop__(self):
        tasks = [
            t for t in asyncio.all_tasks()
            if t is not asyncio.current_task()
        ]
        for t in tasks:
            t.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    def __thread_runner__(self) -> None:
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.create_task(self.__run__())
        self.event_loop.run_forever()

    @abstractmethod
    async def __run__(self) -> None:
        pass