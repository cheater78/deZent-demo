from typing import Any, Callable

from deZent_demo.utils.config.config import *
from deZent_demo.instrument.instrumentor import *
from deZent_demo.ui.widget.control_overlay.control_overlay import *

@dataclass
class Trigger():
    pass

@dataclass
class InstrumentationTrigger(Trigger):
    event: InstrumentEvent

@dataclass
class PresentationState():
    button_action: Callable[..., Any]

@dataclass
class PresentationEvent():
    trigger: Trigger
    state: PresentationState

@dataclass
class PresentationConfig(Config):
    pass



initial = ControlOverlayContent(
    "Initial Setup",
    "All participating gateways form a ring.\nOne of them is (s)elected as coordinator (CCC).",
    "Next: Create counting structure",
    "-> / Go / Next / or non-generic?"
)