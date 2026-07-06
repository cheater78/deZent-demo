#!/usr/bin/env python3
from deZent_demo.network.net_node import VirtualNetwork, VirtualNetworkNode
from deZent_demo.zanon.deZent_gateway import *
from deZent_demo.utils.time_env import *
from deZent_demo.ui.demo_app import *

def print_values(*args: Any) -> None:
    line: str = ""
    for value in args:
        if line:
            line += ", "
        if isinstance(value, CBloomFilter):
            value.print_cnt_struct()
            line += f"CBF"
        else:
            line += f"{value}"
    print(line)

instrumentor = deZentGatewayInstrumentionInfo(
    ccc_round_begin_cb = print_values,
    ccc_round_end_cb = print_values,
    ccc_collection_round_begin_cb = print_values,
    ccc_collection_round_end_cb = print_values,
    ccc_publication_round_begin_cb = print_values,
    ccc_publication_round_end_cb = print_values,
    collection_round_cb = print_values,
    publication_round_cb = print_values,
)

def main():
    # main entry point -> start ce and gws
    try:
        #vnet = VirtualNetwork()
#
        #start_time: datetime = datetime.fromisoformat("2026-01-01")
        #time_env: AbstractTimeEnv = SimTimeEnv(start_time)
#
        #n_gws: int = 2
        #l_gws: list[deZentGateway] = []
#
        #ce_id: NetworkNodeID = n_gws
        #ce_net_node = VirtualNetworkNode(
        #    vnet,
        #    node_id = ce_id
        #)
#
        #for i_gw in range(n_gws):
        #    gw_net_node = VirtualNetworkNode(
        #        vnet,
        #        node_id = i_gw
        #    )
        #    dz_gw: deZentGateway = deZentGateway(
        #        time_env,
        #        gw_net_node,
        #        dt_minutes=121,
        #        z=2,
        #        ce=ce_id,
        #        prev=(i_gw - 1) if i_gw > 0 else (n_gws - 1),
        #        next=(i_gw + 1) if i_gw < n_gws else 0,
        #        instrumentation_info=instrumentor
        #    )
        #    l_gws.append(dz_gw)
#
        #ce_net_node.write(
        #    0,
        #    MessageDeZentRoundBegin(start_time)
        #)

        app = DemoApp()
        app.run()

        # keepalive()
        #vnet.stop()
    except KeyboardInterrupt:
        pass
    except:
        raise
    finally:
        pass
    return 0

if __name__ == "__main__":
    main()