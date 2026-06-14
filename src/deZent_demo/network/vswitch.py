#!/usr/bin/env python3
from deZent_demo.utils.sys import run, sys_ensure_root, sys_netns_exists, sys_iface_exists

class VSwitch():
    '''
    L2 virtual switch,
    creates a netns give by net_name
    allows to attach eth cables by specifying a host if
    '''

    def __init__(self,
                 net_name: str = "deZent-net",
                 net_interface: str = "deZent-vswitch") -> None:
        sys_ensure_root()

        self.net_ns = net_name
        self.bridge = net_interface

    def open(self) -> None:
        self.__netns_create__()

    def close(self) -> None:
        if sys_netns_exists(self.net_ns):
            self.__netns_remove__()
        

    def attach_cable(self, ifname: str) -> None:
        if not sys_netns_exists(self.net_ns):
            raise RuntimeError(f"VSwitch: {self.net_ns} does not exist.")
        if sys_iface_exists(ifname):
            self.__netns_remove_cable__(ifname)
        self.__netns_create_cable__(ifname)

    def exec_ns(self, cmd: list[str], check: bool = True) -> list[str]:
        return run(["ip", "netns", "exec", self.net_ns] + cmd, check)

    def __netns_create__(self) -> None:
        if sys_netns_exists(self.net_ns) or sys_iface_exists(self.bridge, self.net_ns):
            self.__netns_remove__()
        run(["ip", "netns", "add", self.net_ns])
        self.exec_ns(["ip", "link", "set", "lo", "up"])
        self.exec_ns(["ip", "link", "add", self.bridge, "type", "bridge"])
        self.exec_ns(["ip", "link", "set", self.bridge, "up"])
    
    def __netns_remove__(self):
        run(["ip", "netns", "del", self.net_ns], False)
    
    def __netns_create_cable__(self, ifname: str) -> None:
        switch_ifname_peer: str = f"{ifname}-sw"
        # create veth pair
        run([ "ip", "link", "add", ifname, "type", "veth", "peer", "name", switch_ifname_peer ])
        # move switch_ifname_peer into ns
        run([ "ip", "link", "set", switch_ifname_peer, "netns", self.net_ns])
        # connect switch_ifname_peer to switch bridge
        self.exec_ns([ "ip", "link", "set", switch_ifname_peer, "master", self.bridge ])
        # bring switch_ifname_peer up
        self.exec_ns([ "ip", "link", "set", switch_ifname_peer, "up" ])
        # bring ifname up
        run([ "ip", "link", "set", ifname, "up" ])
        
        print(f"\nCreated VSwitch IF {ifname} <- eth cable -> {switch_ifname_peer} - {self.bridge}.\n")

    def __netns_remove_cable__(self, ifname: str) -> None:
        run([ "ip", "link", "del", ifname ])
        
        print(f"\nRemoved VSwitch IF {ifname}.\n")


