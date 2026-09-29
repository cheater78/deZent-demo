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

        self.__init_window_size()
        self.__init_ui()
        self.__init_debug_hotkeys()

        self.create_sandbox()
        cast(NetworkGraphNode, self._network_graph_central_entity).set_center_pos(QPointF(0.0, 0.0))
        NetworkGraph.arrange_ring(
            list[NetworkGraphNode](self._network_graph_gateways.values()),
            QPointF(0.0, 0.0),
            QSizeF(300, 300)
        )

        self.__init_demo_logic()
    
    def __init_window_size(self) -> None:
        screen = self.screen()
        geometry = screen.availableGeometry()

        width = int(geometry.width() * 0.7)
        height = int(geometry.height() * 0.7)

        self.resize(width, height)
        self.move(
            geometry.x() + (geometry.width() - width) // 2,
            geometry.y() + (geometry.height() - height) // 2,
        )

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

        QShortcut(QKeySequence(Qt.Key.Key_Space), self).activated.connect(self._control_overlay.next_button().click)

################################################################################################################################
# NOTE: turn back traveler, these roads will rob you of your will to live
################################################################################################################################
    
    def __init_demo_logic(self) -> None:
        # NOTE: I'm truly sorry for this - didn't have time for a proper architecture
        self.__init_demo_logic_gw1()
        self.__init_demo_logic_gw2()

    def __init_demo_logic_gw1(self) -> None:
        # GW 1
        gw1_id: NetworkNodeID = 1
        gw1: deZentGateway = self._dZ_gws[gw1_id]
        gw1_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw1_id])
        gw1_instrumentor: dZGWInstrumentor = dZGWInstrumentor()

        # Step 0: deZent round begins
        gw1_instrumentor_round_begin_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw1_on_ccc_round_begin_next():
            gw1_instrumentor_round_begin_gate.release()

        def gw1_on_ccc_round_begin(timestamp: datetime):
            self._cbf_plot_widget.setVisible(False)
            self._network_graph_widget.fit_scene_in_view()

            gw1_node.set_coordinator(True)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    "deZent round begins",
                    "A coordinator is picked, which starts the round.",
                    "Create CBF and add inital noise",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_ccc_round_begin_next)
        
        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_BEGIN,
            gw1_on_ccc_round_begin
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_ROUND_BEGIN,
            gw1_instrumentor_round_begin_gate
        )

        # Step 1: cbf noise added
        gw1_instrumentor_cbf_noise_added_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw1_on_cbf_noise_added_next():
            gw1_node.set_coordinator(True)
            gw1_node.set_interaction(False)
            gw1_instrumentor_cbf_noise_added_gate.release()

        def gw1_on_cbf_noise_added(timestamp: datetime, cbf: CBloomFilter, noise: list[int]):
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

            node_interaction()
        
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
            next_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
            gw1_node.next_gw_edge().set_style(next_edge_style)

            self._cbf_plot_widget.hide() # hide cbf
            self._network_graph_widget.fit_scene_in_view() # and re-center view

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            gw1_on_collection_message
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.GW_SEND_COLLECTION_TO_NEXT,
            gw1_instrumentor_collection_message_gate
        )

        # Step 4: collection round is completed, cbf arrives at CCC
        gw1_instrumentor_ccc_collection_round_end_gate: QtInstrumentorGate = QtInstrumentorGate()
        
        def gw1_on_ccc_collection_round_end(timestamp: datetime, cbf: CBloomFilter):
            gw1_node.set_interaction(False)
            gw1_node.set_interaction_cb(None)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    "Collection round completed",
                    "CBF is transferred along the ring and all Gateways add their received measurements to the CBF until it arrives back at the CCC.",
                    "CBF arrives at CCC",
                    "Next"
                )
            )

            for i in range(self._sim_config.n_gws - 1): 
                gw_id: NetworkNodeID = i + 2
                gwi_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw_id])

                gwi_node.set_interaction(False)

                next_edge_style = gwi_node.next_gw_edge().get_style()
                next_edge_style.edge_arrow_style.angle = 45
                next_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
                gwi_node.next_gw_edge().set_style(next_edge_style)

            self._cbf_plot_widget.hide() # hide cbf
            self._network_graph_widget.fit_scene_in_view() # and re-center view

            def gw1_on_ccc_collection_round_end_next():
                # clean up
                for i in range(self._sim_config.n_gws - 1): 
                    gw_id: NetworkNodeID = i + 2
                    gwi_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw_id])
                    gwi_node.set_interaction(False)
                    gwi_node.next_gw_edge().set_style(NetworkGraphEdgeStyle())

                #Step 5.a: CCC removes the inital noise from the CBF
                def gw1_on_ccc_remove_initial_noise_next():
                    gw1_instrumentor_ccc_collection_round_end_gate.release()

                gw1_node.set_interaction(True)
                def node_interaction_pre_remove_noise():
                    self.show_cbf_of(1, cbf)
                gw1_node.set_interaction_cb(node_interaction_pre_remove_noise)

                self._control_overlay.set_content(
                    ControlOverlayContent(
                        "CCC receives the CBF",
                        "The CBF was passed around the ring each GW adding their received measurements by key. The CBF also still contains the noise added at the beginning.",
                        "Remove initial noise",
                        "Next"
                    )
                )
                self._control_overlay.next_button().clicked.connect(gw1_on_ccc_remove_initial_noise_next)

                node_interaction_pre_remove_noise()

            self._control_overlay.next_button().clicked.connect(gw1_on_ccc_collection_round_end_next)
        
        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END,
            gw1_on_ccc_collection_round_end
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END,
            gw1_instrumentor_ccc_collection_round_end_gate
        )

        # Step 5.b: CCC removes the inital noise from the CBF - done
        # Step 6.a pre ensure Z
        gw1_instrumentor_cbf_noise_removed_gate: QtInstrumentorGate = QtInstrumentorGate()

        def gw1_on_ccc_cbf_noise_removed(timestamp: datetime, cbf: CBloomFilter, noise: list[int]):
            self._control_overlay.set_content(
                ControlOverlayContent(
                    "CCC removed the inital noise from CBF",
                    f"Now the CBF contains all measurements without initial noise. " \
                    f"Next all values occuring less than z times are removed.",
                    f"Anonymize values",
                    "Next"
                )
            )

            gw1_node.set_interaction(True)
            def node_interaction_post_remove_noise():
                self.show_cbf_of(1, cbf)
                self._cbf_plot_widget.plot().set_ensure_z_hline(self._deZent_config.z)
            gw1_node.set_interaction_cb(node_interaction_post_remove_noise)

            self._control_overlay.next_button().clicked.connect(gw1_instrumentor_cbf_noise_removed_gate.release)

            node_interaction_post_remove_noise()

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED,
            gw1_on_ccc_cbf_noise_removed
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_NOISE_REMOVED,
            gw1_instrumentor_cbf_noise_removed_gate
        )

        # Step 6.b: ensured min Z
        gw1_instrumentor_ensured_min_z_gate: QtInstrumentorGate = QtInstrumentorGate()

        def gw1_on_ensured_min_z(timestamp: datetime, cbf: CBloomFilter, z: int):
            self._control_overlay.set_content(
                ControlOverlayContent(
                    "Anonymized values",
                    f"The CCC ensured that only values that occurred at least z times are kept for publication by reducing counts by z-1." \
                    f"All remaining values occuring in the CBF can be published.",
                    f"Start Publication",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_instrumentor_ensured_min_z_gate.release)

            gw1_node.set_interaction(True)
            def node_interaction_post_ensure_z():
                self.show_cbf_of(1, cbf)
                self._cbf_plot_widget.plot().set_ensure_z_hline(None)
            gw1_node.set_interaction_cb(node_interaction_post_ensure_z)

            node_interaction_post_ensure_z()

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED,
            gw1_on_ensured_min_z
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_COLLECTION_ROUND_END_CBF_Z_ENSURED,
            gw1_instrumentor_ensured_min_z_gate
        )

        # Step 7: Start publication round
        gw1_instrumentor_start_pub_gate: QtInstrumentorGate = QtInstrumentorGate()

        def gw1_on_start_pub_next() -> None:
            gw1_node.next_gw_edge().set_style(NetworkGraphEdgeStyle())
            gw1_node.set_interaction(False)
            gw1_instrumentor_start_pub_gate.release()
        
        def gw1_on_start_pub(timestamp: datetime, cbf: CBloomFilter, p_pub: float):
            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"CCC starts publication",
                    f"CCC starts the publication round by sending the noiseless anonymized CBF to the next GW.",
                    f"Publication at GW 2",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_start_pub_next)

            gw1_node.set_interaction(False)
            next_edge_style = gw1_node.next_gw_edge().get_style()
            next_edge_style.edge_arrow_style.angle = 45
            next_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
            gw1_node.next_gw_edge().set_style(next_edge_style)

            self._network_graph_widget.fit_scene_in_view()

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN,
            gw1_on_start_pub
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_BEGIN,
            gw1_instrumentor_start_pub_gate
        )

        # Step 9: Complete Publication round
        gw1_instrumentor_complete_publication_gate: QtInstrumentorGate = QtInstrumentorGate()
        
        def gw1_on_complete_publication_next() -> None:
            for i in range(self._sim_config.n_gws - 1): 
                gw_id: NetworkNodeID = i + 2
                gwi_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw_id])

                gwi_node.set_interaction(False)
                gwi_node.next_gw_edge().set_style(NetworkGraphEdgeStyle())
                next_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, gwi_node.next_gw_edge().end_node())
                next_node.ce_edge().set_style(NetworkGraphEdgeStyle())

            gw1_node.set_interaction(False)
            gw1_instrumentor_complete_publication_gate.release()
        
        def gw1_on_complete_publication(
            timestamp: datetime,
            cbf: CBloomFilter,
            p_pub: float,
            publication_fully_finished: bool,
        ) -> None:
            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"Publication round completed",
                    f"All GWs veryfied their publications using the CBF, which now arrives back at the CCC.",
                    f"End round",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_complete_publication_next)

            gw1_node.set_interaction(False)
            for i in range(self._sim_config.n_gws - 1): 
                gw_id: NetworkNodeID = i + 2
                gwi_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw_id])

                gwi_node.set_interaction(False)

                next_edge_style = gwi_node.next_gw_edge().get_style()
                next_edge_style.edge_arrow_style.angle = 45
                next_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
                gwi_node.next_gw_edge().set_style(next_edge_style)

                next_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, gwi_node.next_gw_edge().end_node())
                ce_edge_style = next_node.ce_edge().get_style()
                ce_edge_style.edge_arrow_style.angle = 45
                ce_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
                next_node.ce_edge().set_style(ce_edge_style)

            self._network_graph_widget.fit_scene_in_view()

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END,
            gw1_on_complete_publication
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_PUBLICATION_ROUND_END,
            gw1_instrumentor_complete_publication_gate
        )

        # Step 10: Round end
        gw1_instrumentor_round_end_gate: QtInstrumentorGate = QtInstrumentorGate()
        
        def gw1_on_round_end_next() -> None:
            gw1_instrumentor_complete_publication_gate.release()
            self.close() # TODO: allow more rounds
        
        def gw1_on_round_end(
            timestamp: datetime,
        ) -> None:
            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"deZent Round end",
                    f"Collection and publication are completed, next round starts with the upcoming measurement interval.",
                    f"Close demonstrator",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw1_on_round_end_next)

            gw1_node.set_interaction(False)
            gw1_node.set_coordinator(False) # NOTE: technically not yet
            self._network_graph_widget.fit_scene_in_view()

        gw1_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.CCC_ROUND_END,
            gw1_on_round_end
        )
        gw1_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.CCC_ROUND_END,
            gw1_instrumentor_round_end_gate
        )

        gw1.set_instrumentor(gw1_instrumentor)

    def __init_demo_logic_gw2(self) -> None:
        # GW 2
        gw2_id: NetworkNodeID = 2
        gw2: deZentGateway = self._dZ_gws[gw2_id]
        gw2_node: NetworkGraphGatewayNode = cast(NetworkGraphGatewayNode, self._network_graph_gateways[gw2_id])
        gw2_instrumentor: dZGWInstrumentor = dZGWInstrumentor()

        # Step 3: GW2 collects measurements, shows adding one 
        gw2_on_collection_instrumentor_gate: QtInstrumentorGate = QtInstrumentorGate()
        def gw2_on_collection_next():
            self._cbf_plot_widget.hide()
            gw2_on_collection_instrumentor_gate.release()

        def gw2_on_collection(timestamp: datetime, cbf: CBloomFilter, record_log: RecordLog):
            # cbf arrived at gw2 - nothing added yet
            if not record_log:
                raise RuntimeError(f"record_log was empty")
            
            representative_log_entry: tuple[MeasurementKey, RecordLogDictEntry] = record_log.items()[0]
            representative_m_key: MeasurementKey = representative_log_entry[0]

            gw2_node.set_interaction(True)

            def node_interaction():
                self.show_cbf_of(2, cbf, representative_m_key)
            gw2_node.set_interaction_cb(node_interaction)

            def gw2_on_collection_add_representative_measurement() -> None:
                cbf.add(representative_m_key) # simulate adding the demo key, since all measurements are batched in the real impl
                
                gw2_node.set_interaction(True)
                
                def node_interaction_key_counted():
                    self.show_cbf_of(2, cbf, representative_m_key)
                gw2_node.set_interaction_cb(node_interaction_key_counted)

                self._control_overlay.set_content(
                    ControlOverlayContent(
                        f"GW {gw2_id} adds a measurement to the CBF",
                        f"GW {gw2_id} uses the CBF's {cbf.k} hash functions to determine the indices at which the measurement with key {representative_m_key} should be added. The Measurement increases the counter of these indices by 1.",
                        "Complete Collection round",
                        "Next"
                    )
                )
                self._control_overlay.next_button().clicked.connect(gw2_on_collection_next)

                node_interaction_key_counted()

            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"GW {gw2_id} starts collection",
                    f"GW {gw2_id} receives the CBF, starts collecting SM measurements, and prepares to add the Measurements the the CBF.",
                    f"Add measurement with Key {representative_m_key} to CBF",
                    "Next"
                )
            )
            self._control_overlay.next_button().clicked.connect(gw2_on_collection_add_representative_measurement)

            node_interaction() # open cbf view automatically
        
        gw2_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED,
            gw2_on_collection
        )
        gw2_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.GW_ON_COLLECTION_ROUND_SM_MEASUREMENTS_COLLECTED,
            gw2_on_collection_instrumentor_gate
        )

        # Step 8.a: Publication - failing value
        gw2_on_publication_gate: QtInstrumentorGate = QtInstrumentorGate()

        def gw2_on_publication(
            curr_round_time: datetime,
            cbf: CBloomFilter,
            record_log: RecordLog, # of the gw
            recs2pub: PubLog, # not yet published
            p_pub: float
        ) -> None:
            failing_key: MeasurementKey = 0x0C780000 # big number, which isn't in the data
            failing_key_abort: int = 0xFFFF
            while cbf.check(failing_key):
                failing_key = random.randint(0, 0xFFFFFFFF)
                if failing_key_abort < 0:
                    raise RuntimeError(f"failed to find failing CBF Key") # hopes and prayers that no one will see this
                failing_key_abort -= 1

            gw2_node.set_interaction(True)
            def node_interaction_failing_pub_key():
                self.show_cbf_of(2, cbf, failing_key)
            gw2_node.set_interaction_cb(node_interaction_failing_pub_key)

            self._control_overlay.set_content(
                ControlOverlayContent(
                    f"GW {gw2_id} doesnt publish",
                    f"GW {gw2_id} prevents publication of key {failing_key}, because it does not appear in the CBF. A key absent from the CBF means it wasn't collected atleast z-1 times.",
                    f"Publish another value",
                    "Next"
                )
            )

            # mark "non conductive" - "gw prevents pub"
            ce_edge_style = gw2_node.ce_edge().get_style()
            ce_edge_style.edge_arrow_style.angle = 0 # no arrow wings
            ce_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.darkRed))
            gw2_node.ce_edge().set_style(ce_edge_style)

            # Step 8.b: Publication - succeeding value
            def gw2_on_publication_next():
                # find successful key
                successful_key: MeasurementKey = -1
                for pub_entry in recs2pub:
                    m_key: MeasurementKey = pub_entry.key
                    if cbf.check(m_key):
                        successful_key = m_key
                        break
                
                if successful_key < 0:
                    # no key to publish found -> rig the game
                    rigged_key: MeasurementKey = 0xde2e147 # any key that will be added
                    cbf.add(rigged_key) # adding once is enough, z ensured alr
                    successful_key = rigged_key

                gw2_node.set_interaction(True)
                def node_interaction_successful_pub_key():
                    self.show_cbf_of(2, cbf, successful_key)
                gw2_node.set_interaction_cb(node_interaction_successful_pub_key)

                self._control_overlay.set_content(
                    ControlOverlayContent(
                        f"GW {gw2_id} can publish",
                        f"GW {gw2_id} finds key {successful_key} in the CBF meaning it was collected atleast z times allowing for publication.",
                        f"Complete publication round",
                        "Next"
                    )
                )

                ce_edge_style = gw2_node.ce_edge().get_style()
                ce_edge_style.edge_arrow_style.angle = 45
                ce_edge_style.edge_arrow_style.line_style.pen.setColor(QColor(Qt.GlobalColor.blue))
                gw2_node.ce_edge().set_style(ce_edge_style)

                def gw2_on_publication_done():
                    gw2_node.ce_edge().set_style(NetworkGraphEdgeStyle())
                    gw2_on_publication_gate.release()

                self._control_overlay.next_button().clicked.connect(gw2_on_publication_done)

                node_interaction_successful_pub_key()

            self._control_overlay.next_button().clicked.connect(gw2_on_publication_next)

            node_interaction_failing_pub_key()

        gw2_instrumentor.set_instrument_callback(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH,
            gw2_on_publication
        )
        gw2_instrumentor.set_instrument_gate(
            dZGWInstrumentEvent.GW_ON_PUBLICATION_ROUND_RECORDS_TO_PUBLISH,
            gw2_on_publication_gate
        )

        gw2.set_instrumentor(gw2_instrumentor)

################################################################################################################################
# NOTE: rest easy, you got through
################################################################################################################################

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
        new_style: PresentationSandboxWindowStyle | None = None
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
            gw.get_instrumentor().shutdown_gates()
        super().sim_stop()