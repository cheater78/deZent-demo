#!/usr/bin/env python3
import argparse
import sys
from time import sleep
from deZent_demo.network.vswitch import VSwitch
from deZent_demo.network.net_node import NetworkNode, NetworkNodeID, Message
from deZent_demo.network.dhcp import DHCPServer
from deZent_demo.utils.sys import run_in_term, keepalive

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--virtual", action="store_true", help="Creates a virtual network and spawns the CE + GWs inside it.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gw", action="store_true", help="Gateway mode")
    group.add_argument("--ce", action="store_true", help="CE mode")
    group.add_argument("--op", action="store_true", help="Operator mode")
    parser.add_argument("netif", nargs="?", default=None, help="Network interface")
    args = parser.parse_args()

    use_vnet: bool = args.virtual

    if args.gw or args.ce:
        if not args.netif:
            raise RuntimeError(f"{"GW" if args.gw else "CE"} requires a specified IF!")
        # L2
        net_if: str = args.netif

        if use_vnet:
            print("Attaching to VSwitch...")
            vnet = VSwitch()
            vnet.attach_cable(net_if)
        
        def on_msg(sender: NetworkNodeID, msg: Message) -> None:
            print(f"Message from {sender}: {msg}")
        cert_name: str = net_if
        node: NetworkNode = NetworkNode(net_if, on_msg, cert_name)

        try:
            while True:
                sleep(1)
                node.write(peer, f"Hello from {net_if}".encode())
        except KeyboardInterrupt:
            pass
        except:
            raise
        return 0
    elif args.op:
        if not args.netif:
            raise RuntimeError(f"Net OP requires a specified IF!")

        net_if: str = args.netif

        dhcp_server = DHCPServer(net_interface=net_if) # TODO: pull out netns logic
        try:
            dhcp_server.open()
            
            # TODO: run net op here
            # CA, P2P bootstrap node
            keepalive() 
        except KeyboardInterrupt:
            pass
        except:
            raise
        finally:
            dhcp_server.close()
    else:
        if not use_vnet:
            raise RuntimeError(f"Cannot run dev env without --virtual!")
        # L2
        print("Creating VSwitch...")
        vnet = VSwitch() # TODO: VSwitch.run?

        # main entry point -> start ce and gws
        try:
            vnet.open()
            # start net op
            op_if: str = vnet.bridge
            # TODO: run in netns if virtual
            run_in_term([sys.executable, "-m", "deZent_demo", "--virtual", "--op", op_if])

            # start ce
            ce_if: str = f"deZent-ce"
            run_in_term([sys.executable, "-m", "deZent_demo", "--virtual", "--ce", ce_if])

            # start gws
            n_gws: int = 2
            for i_gw in range(n_gws):
                i_gw_if: str = f"deZent-gw-{i_gw}"
                run_in_term([sys.executable, "-m", "deZent_demo", "--virtual", "--gw", i_gw_if])
            keepalive() # TODO: run net op here            
        except KeyboardInterrupt:
            pass
        except:
            raise
        finally:
            vnet.close()
        return 0

if __name__ == "__main__":
    main()