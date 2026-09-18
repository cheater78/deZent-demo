from __future__ import annotations
from dataclasses import dataclass
from typing import override
from deZent_demo.sandbox.presentation_sandbox import *
from deZent_demo.view.control_overlay.control_overlay import ControlOverlay
from deZent_demo.view.counting_bloom_filter.counting_bloom_filter_view import CountingBloomFilterView
from deZent_demo.view.network_graph.network_graph_view import NetworkGraphView
from deZent_demo.view.style.style import Style, Styled

from .window import SandboxWindow

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QResizeEvent, QKeySequence, QShortcut

@dataclass
class PresentationWindowStyle(Style):
    title: str = "deZent Presentation"
    left_column_relative: float = 0.33
    left_column_top_relative: float = 0.10
    full_outer_margin_relative: float = 0.03

class PresentationWindow(Styled[PresentationWindowStyle], SandboxWindow):
    
    class _OverlayHost(QWidget):
        
        def __init__(self, window: PresentationWindow):
            super().__init__()
            self._window = window

        def resizeEvent(self, event: QResizeEvent) -> None:
            super().resizeEvent(event)
            self._window.layout_overlay(self.size())
    
    def __init__(
        self,
        style: PresentationWindowStyle = PresentationWindowStyle(),
        **kwargs: Any,
    ) -> None:
        
        self._ctrl_overlay = ControlOverlay()
        self._cbf_view = CountingBloomFilterView()
        self._network_graph_view = NetworkGraphView()

        sandbox = PresentationSandbox(
            self._ctrl_overlay,
            self._cbf_view,
            self._network_graph_view
        )

        self._main_widget = PresentationWindow._OverlayHost(self)
        super().__init__(
            style=style,
            sandbox=sandbox,
            **kwargs
        )
        self.setCentralWidget(self._main_widget)

        self._network_graph_view.setParent(self._main_widget)
        self._network_graph_view.setGeometry(0, 0, 1, 1)
        self._network_graph_view.lower()

        self._ctrl_overlay.setParent(self._main_widget)
        self._cbf_view.setParent(self._main_widget)

        self._ctrl_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._ctrl_overlay.setAutoFillBackground(True)
        self._ctrl_overlay.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._cbf_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._cbf_view.setAutoFillBackground(True)
        self._cbf_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._ctrl_overlay.raise_()
        self._cbf_view.raise_()

        self.showMaximized()

        #TODO: debug
        def toggle():
            self._cbf_view.setVisible(not self._cbf_view.isVisible())
        QShortcut(QKeySequence('T'), self).activated.connect(toggle)

    @override
    def on_style_change(self, new_style: PresentationWindowStyle):
        self.setWindowTitle(new_style.title)
        self.layout_overlay(self._main_widget.size(), new_style)
    
    def toggle_cbf_view(self, visible: bool):
        self._cbf_view.setVisible(visible)
        self.layout_overlay(self.size())
    
    def layout_overlay(
        self,
        size: QSize,
        new_style: PresentationWindowStyle | None = None,
    ) -> None:
        w = max(1, size.width())
        h = max(1, size.height())

        self._network_graph_view.setGeometry(0, 0, w, h)

        style: PresentationWindowStyle = new_style if new_style is not None else self.get_style()

        left_column_width = int(w * style.left_column_relative)
        full_outer_margin_w = int(w * style.full_outer_margin_relative)
        full_outer_margin_h = int(h * style.full_outer_margin_relative)
        top_height = int(h * style.left_column_top_relative - style.full_outer_margin_relative)
        right_panel_width = int(w * (1 - style.left_column_relative - style.full_outer_margin_relative))
        right_panel_height = int(h * (1 - 2 * style.full_outer_margin_relative))

        self._ctrl_overlay.setGeometry(
            full_outer_margin_w,
            full_outer_margin_h,
            max(1, left_column_width - full_outer_margin_w),
            max(1, top_height)
        )
        self._cbf_view.setGeometry(
            left_column_width,
            full_outer_margin_h,
            max(1, right_panel_width),
            max(1, right_panel_height)
        )

        self._network_graph_view.lower()
        self._ctrl_overlay.raise_()
        self._cbf_view.raise_()