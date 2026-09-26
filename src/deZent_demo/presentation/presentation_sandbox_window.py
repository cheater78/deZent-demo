from __future__ import annotations
from dataclasses import dataclass
from typing import override, cast

from deZent_demo.network import *
from deZent_demo.sandbox.sandbox import *
from deZent_demo.ui.widget.layer_stack_widget import *
from deZent_demo.ui.widget.control_overlay.control_overlay import *
from deZent_demo.ui.widget.counting_bloom_filter.counting_bloom_filter_widget import *
from deZent_demo.ui.widget.network_graph.network_graph import *
from deZent_demo.ui.widget.network_graph.network_graph_widget import *
from deZent_demo.ui.style.style import Style, Styled
from deZent_demo.ui.window.sandbox_window import SandboxWindow

from PySide6.QtCore import (
    Qt,
    QPointF,
    QSize, QSizeF,
)
from PySide6.QtWidgets import (
    QWidget
)
from PySide6.QtGui import (
    QResizeEvent,
    QKeySequence,
    QShortcut
)

@dataclass
class PresentationSandboxWindowConfig(Config):
    deZent_config: deZentConfig = field(default_factory=lambda: deZentConfig())
    sim_config: SimConfig = field(default_factory=lambda: SimConfig())

@dataclass
class PresentationSandboxWindowStyle(Style):
    title: str = "deZent Presentation"

    left_column_relative: float = 0.33
    left_column_top_relative: float = 0.15
    full_outer_margin_relative: float = 0.03

    control_overlay_style: ControlOverlayStyle = field(default_factory=lambda: ControlOverlayStyle())
    cbf_plot_widget_style: CBFPlotWidgetStyle = field(default_factory=lambda: CBFPlotWidgetStyle())
    network_graph_widget: NetworkGraphWidgetStyle = field(default_factory=lambda: NetworkGraphWidgetStyle())

class PresentationSandboxWindow(Styled[PresentationSandboxWindowStyle], SandboxWindow):
    
    def __init__(
        self,
        config: PresentationSandboxWindowConfig = PresentationSandboxWindowConfig(),
        style: PresentationSandboxWindowStyle = PresentationSandboxWindowStyle(),
        **kwargs: Any,
    ) -> None:
        self._main_widget: QWidget = LayerStackWidget()
        
        self._control_overlay = ControlOverlay()
        self._cbf_plot_widget = CBFPlotWidget()
        self._network_graph_widget = NetworkGraphWidget()

        self._network_graph_central_entity: NetworkGraphNode | None = None
        self._network_graph_gateways: dict[NetworkNodeID, NetworkGraphNode] = { }

        super().__init__(
            style=style,
            deZent_config=config.deZent_config,
            sim_config=config.sim_config,
            **kwargs,
        )

        self._main_widget.set_resize_cb(self.on_main_widget_resize)
        self.setCentralWidget(self._main_widget)

        self._main_widget.makeLayer(self._network_graph_widget)
        self._network_graph_widget.setGeometry(0, 0, 1, 1)

        self._main_widget.makeLayer(self._control_overlay)
        self._control_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._control_overlay.setAutoFillBackground(True)
        self._control_overlay.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._main_widget.makeLayer(self._cbf_plot_widget)
        self._cbf_plot_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._cbf_plot_widget.setAutoFillBackground(True)
        self._cbf_plot_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        #TODO: debug
        def toggle():
            self._cbf_plot_widget.setVisible(not self._cbf_plot_widget.isVisible())
        QShortcut(QKeySequence('T'), self).activated.connect(toggle)
        self._network_graph_widget.set_fit_scene_in_view_shortcut(QShortcut(QKeySequence('R'), self))
        #TODO: ~debug

        self.create_sandbox()
        cast(NetworkGraphNode, self._network_graph_central_entity).set_center_pos(QPointF(0.0, 0.0))
        NetworkGraph.arrange_ring(
            list[NetworkGraphNode](self._network_graph_gateways.values()),
            QPointF(0.0, 0.0),
            QSizeF(300, 300)
        )
        self._network_graph_widget.scene().update()
        self._network_graph_widget.fit_scene_in_view()
        self.toggle_cbf_view(False)

        # TODO: debug
        debug_cbf: CBloomFilter = CBloomFilter.create(3, 4)
        for _ in range(78):
            debug_cbf.add(78)
        self._cbf_plot_widget.plot().update_cbf(debug_cbf, debug_cbf.inspect_item_indices(78))

        if False:
            for i in range(self._sim_config.n_gws):
                gw_id: NetworkNodeID = i + 1
                gw: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw_id])
                gw.set_interaction(gw_id == 1)
                gw.set_coordinator(gw_id == 1)
        #TODO: ~debug
        
        def gw1_on_noise_added(timestamp: datetime, cbf: CBloomFilter, noise: int):
            self._cbf_plot_widget.plot().update_cbf(cbf, cbf.inspect_item_indices(noise))

            gw1_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[1])
            gw1_node.set_coordinator(True)
            gw1_node.set_interaction(True)

            def node_interaction():
                self._cbf_plot_widget.show()
                # TODO: fit in view for nodes as well / allow setting an object to a coord -> move view accordingly
            gw1_node.set_interaction_cb(node_interaction)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    "CBF noise added",
                    "Initially the coordinator creates the CBF and adds some arbitrary noise.",
                    "Begin Collection on GW 2",
                    "Next"
                )
            )
        gw1_instrumentor: dZGWInstrumentor = dZGWInstrumentor()
        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            gw1_on_noise_added
        )

        gw1_instrumentor_gate: QtInstrumentorGate = QtInstrumentorGate()
        gw1_instrumentor_gate.gate_signal.connect(self._control_overlay.next_button().clicked)
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            gw1_instrumentor_gate
        )
        self._dZ_gws[1].set_instrumentor(gw1_instrumentor)
    
    @override
    def on_style_change(self, new_style: PresentationSandboxWindowStyle):
        self.setWindowTitle(new_style.title)
        self.layout_overlay(self._main_widget.size(), new_style)
        self._control_overlay.set_style(new_style.control_overlay_style)
        self._cbf_plot_widget.set_style(new_style.cbf_plot_widget_style)
        self._network_graph_widget.set_style(new_style.network_graph_widget)
    
    def toggle_cbf_view(self, visible: bool):
        self._cbf_plot_widget.setVisible(visible)
        self.layout_overlay(self.size())

    # TODO: test resizeEvent on MainWindow - that could just work making LayerStackWidget (resize) obsolete
    def on_main_widget_resize(self, event: QResizeEvent) -> None:
        self.layout_overlay(event.size())
    
    # TODO: cleanup
    def layout_overlay(
        self,
        size: QSize,
        new_style: PresentationSandboxWindowStyle | None = None,
    ) -> None:
        w = max(1, size.width())
        h = max(1, size.height())

        self._network_graph_widget.setGeometry(0, 0, w, h)

        style: PresentationSandboxWindowStyle = new_style if new_style is not None else self.get_style()

        left_column_width = int(w * style.left_column_relative)
        full_outer_margin_w = int(w * style.full_outer_margin_relative)
        full_outer_margin_h = int(h * style.full_outer_margin_relative)
        top_height = int(h * style.left_column_top_relative - style.full_outer_margin_relative)
        right_panel_width = int(w * (1 - style.left_column_relative - style.full_outer_margin_relative))
        right_panel_height = int(h * (1 - 2 * style.full_outer_margin_relative))

        self._control_overlay.setGeometry(
            full_outer_margin_w,
            full_outer_margin_h,
            max(1, left_column_width - full_outer_margin_w),
            max(1, top_height)
        )
        self._cbf_plot_widget.setGeometry(
            left_column_width,
            full_outer_margin_h,
            max(1, right_panel_width),
            max(1, right_panel_height)
        )

        self._network_graph_widget.lower()
        self._control_overlay.raise_()
        self._cbf_plot_widget.raise_()

    @override
    def create_central_entity(self, ce_id: NetworkNodeID):
        if self._network_graph_central_entity is not None:
            raise RuntimeError('create_gateway: ce already exists!')
        
        Sandbox.create_central_entity(self, ce_id)
        self._network_graph_central_entity = self._network_graph_widget.graph().create_node()
        self._network_graph_central_entity.set_label("CE")
    
    @override
    def create_gateway(
        self,
        id: NetworkNodeID,
        ce_id: NetworkNodeID | None = None,
        next_id: NetworkNodeID | None = None,
    ) -> None:
        if self._network_graph_gateways.get(id) is not None:
            raise RuntimeError(f"create_gateway: id={id} already exists!")
        
        Sandbox.create_gateway(self, id, ce_id, next_id)
        network_graph_node = self._network_graph_widget.graph().create_gateway_node()
        network_graph_node.set_label(f"GW {id}")
        self._network_graph_gateways[id] = network_graph_node
    
    @override
    def link_gateway_to_central_entity(self, gw_id: NetworkNodeID):
        if self._network_graph_gateways.get(gw_id) is None \
            or self._network_graph_central_entity is None:
            raise RuntimeError(f"link_gateway_to_central_entity: id={gw_id},ce do not exists!")
        
        Sandbox.link_gateway_to_central_entity(self, gw_id)
        self._network_graph_gateways[gw_id].link_to(self._network_graph_central_entity)

    @override
    def link_gateway_to_gateway(self, from_id: NetworkNodeID, to_id: NetworkNodeID):
        if self._network_graph_gateways.get(from_id) is None \
            or self._network_graph_gateways.get(to_id) is None:
            raise RuntimeError(f"link_gateway_to_gateway: id={from_id},{to_id} do not exists!")
        
        Sandbox.link_gateway_to_gateway(self, from_id, to_id)
        self._network_graph_gateways[from_id].link_to(self._network_graph_gateways[to_id])