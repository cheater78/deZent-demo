from deZent_demo.sandbox.sandbox import *
from PySide6.QtWidgets import QMainWindow

class SandboxWindow(Sandbox, QMainWindow):
    
    def __init__(
        self,
        deZent_config: deZentConfig = deZentConfig(),
        sim_config: SimConfig = SimConfig(),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            deZent_config=deZent_config,
            sim_config=sim_config,
            **kwargs,
        )

