from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import time
import threading
from collections import deque
import heapq

class AbstractTimeEnv(ABC):
    
    @abstractmethod
    def _now_(self) -> datetime:
        pass

    @abstractmethod
    def wait_until(self, time_point: datetime) -> None:
        pass

class RealTimeEnv(AbstractTimeEnv):
    
    def _now_(self) -> datetime:
        return datetime.now()

    def wait_until(self, time_point: datetime) -> None:
        now: datetime = self._now_()
        if time_point <= now:
            return
        remaining_s: float = (time_point - now).total_seconds()
        time.sleep(remaining_s) # yield until time is reached


class SimTimeEnv(AbstractTimeEnv):

    def __init__(self, init_time: datetime) -> None:
        self._lck_ = threading.Lock()
        self._discrete_current_time_: datetime = init_time

        # Min-heap of unique timestamps.
        self._times_: list[datetime] = []
        self._waiters_: dict[datetime, deque[threading.Event]] = {}

    def _now_(self) -> datetime:
        with self._lck_:
            return self._discrete_current_time_

    def wait_until(self, time_point: datetime) -> None:
        event = threading.Event()

        with self._lck_:
            if time_point <= self._discrete_current_time_:
                event.set()
            else:
                if time_point not in self._waiters_:
                    self._waiters_[time_point] = deque()
                    heapq.heappush(self._times_, time_point)

                self._waiters_[time_point].append(event)

        event.wait()

    def advance(self, to: datetime | None = None, by: timedelta | None = None) -> None:
        if to is None and by is None:
            return

        wake_events: list[threading.Event] = []

        # NOTE: the strict ordering is currently unused -> all events are collected and triggerd at once
        with self._lck_:
            time_point: datetime
            if to is not None:
                time_point = to
            elif by is not None:
                time_point = self._discrete_current_time_ + by
            else:
                return # never

            while self._times_ and self._times_[0] <= time_point:
                t = heapq.heappop(self._times_)
                self._discrete_current_time_ = t

                wake_events.extend(self._waiters_.pop(t))

            self._discrete_current_time_ = time_point

        # Wake threads after releasing the lock.
        for event in wake_events:
            event.set()

class NetworkSimTimeEnv(SimTimeEnv):
    pass
