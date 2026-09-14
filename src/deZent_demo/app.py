from typing import ClassVar, override

from .view.control_overlay.control_overlay import ControlOverlay
from .view.counting_bloom_filter.counting_bloom_filter_view import CountingBloomFilterView
from .view.network_graph.network_graph_view import NetworkGraphView

from .sandbox import Sandbox

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
)
from PySide6.QtCore import (
    Qt, QSize,
    QCoreApplication
)


class _OverlayHost(QWidget):
    def __init__(self, app: "App") -> None:
        super().__init__()
        self._app = app

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._app._layout_overlay(self.size())


class App(QApplication):
    title: ClassVar [str] = "deZent demo"

    def __init__(self,
                 /,
                 title: str = title,
                 args: list[str] = []) -> None:
        super().__init__(args)

        self._window_title: str = title
        self._window: QMainWindow = QMainWindow()

        self._ctrl_overlay: ControlOverlay = ControlOverlay()
        self._cbf_view: CountingBloomFilterView = CountingBloomFilterView()
        self._network_graph_view: NetworkGraphView = NetworkGraphView()

        self._sandbox: Sandbox = Sandbox()

        self.__setup_window()

    def __setup_window(self) -> None:
        main_widget: QWidget = _OverlayHost(self)
        self._window.setCentralWidget(main_widget)

        self._network_graph_view.setParent(main_widget)
        self._network_graph_view.setGeometry(0, 0, 1, 1)
        self._network_graph_view.lower()

        self._hud_widget: QWidget = QWidget(main_widget)
        self._hud_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._hud_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._hud_widget.setAutoFillBackground(False)
        self._hud_widget.setStyleSheet("background: transparent; border: none;")
        self._hud_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._hud_widget.setGeometry(0, 0, 1, 1)

        self._ctrl_overlay.setParent(self._hud_widget)
        self._cbf_view.setParent(self._hud_widget)

        self._ctrl_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._ctrl_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._ctrl_overlay.setAutoFillBackground(False)
        self._cbf_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._cbf_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._cbf_view.setAutoFillBackground(False)
        self._ctrl_overlay.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cbf_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._hud_widget.raise_()
        self._ctrl_overlay.raise_()
        self._cbf_view.raise_()

        self._layout_overlay(main_widget.size())

        self._window.setWindowTitle(self._window_title)

    def _layout_overlay(self, size: QSize) -> None:
        if not hasattr(self, "_hud_widget"):
            return

        w: int = max(1, size.width())
        h: int = max(1, size.height())

        self._network_graph_view.setGeometry(0, 0, w, h)
        self._hud_widget.setGeometry(0, 0, w, h)

        left_column_relative: float = 0.385
        left_column_top_relative: float = 0.385
        full_outer_margin_relative: float = 0.02

        left_column_width: int = int(w * left_column_relative)
        full_outer_margin_w: int = int(w * full_outer_margin_relative)
        full_outer_margin_h: int = int(h * full_outer_margin_relative)
        top_height: int = int(h * left_column_top_relative - full_outer_margin_relative)

        right_panel_width: int = int(w * (1.0 - left_column_relative - full_outer_margin_relative))
        right_panel_height: int = int(h * (1.0 - 2 * full_outer_margin_relative))

        self._ctrl_overlay.setGeometry(
            full_outer_margin_w,
            full_outer_margin_h,
            max(1, left_column_width - full_outer_margin_w),
            max(1, top_height),
        )

        self._cbf_view.setGeometry(
            left_column_width,
            full_outer_margin_h,
            max(1, right_panel_width),
            max(1, right_panel_height),
        )

    def toggle_cbf_view(self, visible: bool) -> None:
        self._cbf_view.setVisible(visible)
        self._layout_overlay(self._window.size())

    def __init(self) -> None:
        #self._sandbox.sim_init()
        self._window.show()

    def __fini(self) -> None:
        #self._sandbox.sim_stop()
        pass
    
    @override
    @staticmethod
    def exec() -> int:
        app: App = App.get_instance()
        app.__init()
        
        exit_code: int = 1 # error by default
        try:
            exit_code = QApplication.exec()
        except KeyboardInterrupt:
            print(f"{app._window_title} was cancelled by keyboard interrupt.")
            exit_code = 0
        except:
            raise
        finally:
            app.__fini()

        return exit_code

    @staticmethod
    def get_instance() -> App:
        core_app: QCoreApplication | None = QApplication.instance()
        if core_app is None:
            raise RuntimeError(f"Failed to retrieve the application instance!")
        if not isinstance(core_app, App):
            raise RuntimeError(f"The retrieved application instance was not of type 'App'!")
        return core_app
