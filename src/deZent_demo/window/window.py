from deZent_demo.sandbox.sandbox import Sandbox
from PySide6.QtWidgets import QMainWindow

class SandboxWindow(QMainWindow):
    
    def __init__(
        self,
        sandbox: Sandbox
    ) -> None:
        super().__init__()
        self._sandbox: Sandbox = sandbox
        self.show()
    
    def sandbox_start(self):
        self._sandbox.sim_start()
    
    def sandbox_stop(self):
        self._sandbox.sim_stop()

