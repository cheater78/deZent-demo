from __future__ import annotations
from dataclasses import dataclass
from typing import override, cast

from deZent_demo.network import *
from deZent_demo.sandbox.sandbox import *
from deZent_demo.instrument.instrumentor import *
from deZent_demo.ami.measurement import *
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
    QRect,
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
        self._main_widget: QWidget = QWidget()
        
        self._control_overlay = ControlOverlay()
        self._cbf_plot_widget = CBFPlotWidget()
        self._network_graph_widget = NetworkGraphWidget()

        self._network_graph_central_entity: NetworkGraphNode | None = None
        self._network_graph_gateways: dict[NetworkNodeID, NetworkGraphNode] = { }
        self._instruments: dict[NetworkNodeID, Instrumentor] = { }

        super().__init__(
            style=style,
            deZent_config=config.deZent_config,
            sim_config=config.sim_config,
            **kwargs,
        )

        self.__init_ui()
        self.__init_debug_hotkeys()

        self.create_sandbox()
        cast(NetworkGraphNode, self._network_graph_central_entity).set_center_pos(QPointF(0.0, 0.0))
        NetworkGraph.arrange_ring(
            list[NetworkGraphNode](self._network_graph_gateways.values()),
            QPointF(0.0, 0.0),
            QSizeF(300, 300)
        )
        self._network_graph_widget.fit_scene_in_view()
        self._cbf_plot_widget.setVisible(False)

        self.__init_demo_logic()

    def __init_ui(self) -> None:
        self.setCentralWidget(self._main_widget)
        
        self._network_graph_widget.setParent(self._main_widget)
        self._network_graph_widget.lower()
        self._network_graph_widget.setGeometry(0, 0, 1, 1)

        self._control_overlay.setParent(self._main_widget)
        self._control_overlay.raise_()
        self._control_overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._control_overlay.setAutoFillBackground(True)
        self._control_overlay.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._cbf_plot_widget.setParent(self._main_widget)
        self._cbf_plot_widget.raise_()
        self._cbf_plot_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._cbf_plot_widget.setAutoFillBackground(True)
        self._cbf_plot_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def __init_debug_hotkeys(self) -> None:
        def toggle_cbf_plot():
            self._cbf_plot_widget.setVisible(not self._cbf_plot_widget.isVisible())
        QShortcut(QKeySequence('T'), self).activated.connect(toggle_cbf_plot)

        QShortcut(QKeySequence('R'), self).activated.connect(self._network_graph_widget.fit_scene_in_view)

    def __init_demo_logic(self) -> None:
        # NOTE: I'm truly sorry for this - didn't have time for proper a architecture
        self.__init_demo_logic_gw1()
        self.__init_demo_logic_gw2()

    def __init_demo_logic_gw1(self) -> None:
        # GW 1
        gw1_id: NetworkNodeID = 1
        gw1: deZentGateway = self._dZ_gws[gw1_id]
        gw1_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw1_id])
        gw1_instrumentor: dZGWInstrumentor = dZGWInstrumentor()

        # Step 1: cbf noise added
        gw1_instrumentor_cbf_noise_added_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw1_on_cbf_noise_added_next():
            gw1_node.set_coordinator(True)
            gw1_node.set_interaction(False)
            gw1_instrumentor_cbf_noise_added_gate.release()

        def gw1_on_cbf_noise_added(timestamp: datetime, cbf: CBloomFilter, noise: list[int]):
            self._cbf_plot_widget.plot().update_cbf(cbf)
            gw1_node.set_coordinator(True)
            gw1_node.set_interaction(True)

            def node_interaction():
                self.show_cbf_of(1, cbf)
            gw1_node.set_interaction_cb(node_interaction)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    "CBF noise added",
                    "Initially the coordinator creates the CBF and adds some arbitrary noise.",
                    "Begin Collection Round",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_cbf_noise_added_next)
        
        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            gw1_on_cbf_noise_added
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_BEGIN_CBF_NOISE_ADDED,
            gw1_instrumentor_cbf_noise_added_gate
        )

        # Step 2: CCC starts collection round by sending a message to next
        gw1_instrumentor_collection_message_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw1_on_collection_message_next():
            gw1_node.next_gw_edge().set_style(NetworkGraphEdgeStyle())
            gw1_instrumentor_collection_message_gate.release()

        def gw1_on_collection_message(gw_next_id: NetworkNodeID, message: MessageRoundCollect):
            self._control_overlay.set_content(
                ControlOverlayContent(
                    "Collection Round starts",
                    f"The coordinator starts the collection round by sending the CBF to GW {gw_next_id}",
                    f"Start collection on GW {gw1.get_next()}",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_collection_message_next)
            next_edge_style = gw1_node.next_gw_edge().get_style()
            next_edge_style.edge_arrow_style.angle = 45
            next_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.red))
            gw1_node.next_gw_edge().set_style(next_edge_style)

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            gw1_on_collection_message
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            gw1_instrumentor_collection_message_gate
        )

        gw1.set_instrumentor(gw1_instrumentor)

    def __init_demo_logic_gw2(self) -> None:
        # GW 2
        gw2_id: NetworkNodeID = 2
        gw2: deZentGateway = self._dZ_gws[gw2_id]
        gw2_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw2_id])
        gw2_instrumentor: dZGWInstrumentor = dZGWInstrumentor()

        # Step 3: GW collection round
        gw2_on_collection_instrumentor_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw2_on_collection_next():
            
            gw2_on_collection_instrumentor_gate.release()

        def gw2_on_collection(timestamp: datetime, cbf: CBloomFilter):
            self._cbf_plot_widget.plot().update_cbf(cbf)
            gw2_node.set_interaction(True)

            def node_interaction():
                self.show_cbf_of(2, cbf)
            gw2_node.set_interaction_cb(node_interaction)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"GW {gw2_id} starts collection",
                    f"GW {gw2_id} receives the CBF and starts collecting SM measurements.",
                    "Begin Collection Round",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw2_on_collection_next)

            node_interaction() # open cbf view automatically
        
        gw2_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND,
            gw2_on_collection
        )
        gw2_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND,
            gw2_on_collection_instrumentor_gate
        )

        gw2.set_instrumentor(gw2_instrumentor)

    def show_cbf_of(self, gw_id: NetworkNodeID, cbf: CBloomFilter, value: MeasurementValue | None = None) -> None:
        self._cbf_plot_widget.plot().update_cbf(
            cbf,
            cbf.inspect_item_indices(value) if value is not None 
            else set[int]()
        )
        self._cbf_plot_widget.show()

        graph_rect: QRect = self._network_graph_widget.rect()
        gw_node: NetworkGraphNode = self._network_graph_gateways[gw_id]
        gw_node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

        left_column_hcenter_relative: float = self._style.left_column_relative / 2
        left_column_bot_height_relative: float = (1.0 - self._style.left_column_top_relative) - self._style.full_outer_margin_relative
        left_column_bot_vcenter_relative: float = self._style.left_column_top_relative + (left_column_bot_height_relative / 2)

        self._network_graph_widget.move_scene_to_view(
            gw_node.mapToScene(gw_node.center()),
            graph_rect.topLeft() + QPoint(
                int(graph_rect.width() * left_column_hcenter_relative),
                int(graph_rect.height() * left_column_bot_vcenter_relative),
            )
        )
        gw_node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    @override
    def on_style_change(self, new_style: PresentationSandboxWindowStyle):
        self.setWindowTitle(new_style.title)
        self.layout_overlay(self._main_widget.size(), new_style)
        self._control_overlay.set_style(new_style.control_overlay_style)
        self._cbf_plot_widget.set_style(new_style.cbf_plot_widget_style)
        self._network_graph_widget.set_style(new_style.network_graph_widget)
    
    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        self.layout_overlay(event.size())
        return super().resizeEvent(event)
    
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
    def create_central_entity(
        self,
        ce_id: NetworkNodeID,
    ) -> None:
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

    @override
    def sim_start(self):
        super().sim_start()

    @override
    def sim_stop(self):
        for gw in self._dZ_gws.values():
            gw.get_instrumentor().release_gates()
        super().sim_stop()