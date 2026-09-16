from __future__ import annotations
from typing import override

from .window.window import SandboxWindow
from .window.presentation_window import PresentationWindow

from PySide6.QtCore import (
    QCoreApplication,
)
from PySide6.QtWidgets import (
    QApplication,
)

class App(QApplication):

    def __init__(
        self,
        /,
        args: list[str] | None = None,
    ) -> None:
        super().__init__(args or [])
        self._window: SandboxWindow = PresentationWindow()
    
    def __init(self) -> None:
        self._window.sandbox_start()

    def __fini(self) -> None:
        self._window.sandbox_stop()

    @override
    @staticmethod
    def exec() -> int:
        app: App = App.get_instance()
        app.__init()

        exit_code: int = 1

        try:
            exit_code = QApplication.exec()
        except KeyboardInterrupt:
            print(
                f"{app._window.windowTitle()} was cancelled by keyboard interrupt."
            )
            exit_code = 0
        finally:
            app.__fini()

        return exit_code

    @staticmethod
    def get_instance() -> App:
        core_app: QCoreApplication | None = QApplication.instance()

        if core_app is None:
            raise RuntimeError(
                "Failed to retrieve the application instance!"
            )

        if not isinstance(core_app, App):
            raise RuntimeError(
                "The retrieved application instance was not of type 'App'!"
            )

        return core_app