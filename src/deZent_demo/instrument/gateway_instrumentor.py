from enum import auto
from datetime import datetime

from deZent_demo.network import *
from deZent_demo.ami.measurement_log import RecordLogEntry

from .instrumentor import *

class GWInstrumentEvent(InstrumentEvent):
    GW_COLLECT_SM_MEASUREMENT = auto()

class GWInstrumentor(QtThreadSafeInstrumentor):
    event_type = GWInstrumentEvent
    event_cb_signatures = {
        GWInstrumentEvent.GW_COLLECT_SM_MEASUREMENT: [datetime, NetworkNodeID, RecordLogEntry]
    }