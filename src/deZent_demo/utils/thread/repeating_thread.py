import sys
import threading
from abc import ABC, abstractmethod

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
