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
        self._loop_ready = threading.Event()

        self.thread = threading.Thread(
            target=self.__thread_runner__
        )
        if auto_start:
            self.start()

    def start(self) -> None:
        self.thread.start()
        self._loop_ready.wait() # wait until loop alive

    def stop(self) -> None:
        async def shutdown():
            tasks = [
                t for t in asyncio.all_tasks()
                if t is not asyncio.current_task()
            ]
            print("Cancelling AsyncThread Tasks...")
            for t in tasks:
                t.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)
            
            print("Stopping AsyncThread Eventloop...")
            self.event_loop.stop()

        print("Stopping AsyncThread...")
        future = asyncio.run_coroutine_threadsafe(
            shutdown(),
            self.event_loop,
        )
        print("Waiting for shutdown...")
        future.result()
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

        async def safe_runner():
            try:
                await self.__run__()
            except Exception:
                import traceback
                traceback.print_exc()

        self.event_loop.create_task(safe_runner())
        self._loop_ready.set() # mark loop alive
        self.event_loop.run_forever()

    @abstractmethod
    async def __run__(self) -> None:
        pass