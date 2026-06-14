from time import sleep
from datetime import datetime, timedelta
from typing import Callable

ConditionEvalFunc = Callable[[], bool]
def wait_sync(condition_eval: ConditionEvalFunc, timeout_s: float = 0) -> bool:
    timeout_used: bool = timeout_s != 0
    timeout: timedelta = timedelta(seconds = timeout_s)
    begin: datetime = datetime.now()
    while not condition_eval():
        if timeout_used and datetime.now() - timeout > begin:
            return False
        sleep(0.01)
    return True

