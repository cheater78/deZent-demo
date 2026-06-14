#!/usr/bin/env python3
import os
import signal
from deZent_demo.utils.sys import run_unsafe, run, sys_file_exists, sys_install, IPAddr, sys_if_ip_addr
from typing import cast

dhcp_server_dependecies: dict[str, list[str]] = {
    "debian": ["iproute2", "dnsmasq"],
    "arch": ["iproute2", "dnsmasq"],
}

network_client_dependecies: dict[str, list[str]] = {
    "debian": ["dhclient"],
    "arch": ["dhclient"],
}

class DHCPServer():

    def __init__(self,
                 net_name: str = "deZent-net",
                 net_interface: str = "eth0",
                 listen_ip: IPAddr = "10.0.0.1",
                 net_pre_len: int = 24,
                 dhcp_begin: IPAddr = "10.0.0.100",
                 dhcp_end: IPAddr = "10.0.0.200",
                 dhcp_ttl: str = "96h") -> None:
        self.net_name = net_name
        self.net_if = net_interface
        self.net_pre_len = net_pre_len
        self.ip_addr = listen_ip
        self.dhcp_begin = dhcp_begin
        self.dhcp_end = dhcp_end
        self.dhcp_ttl = dhcp_ttl

        self.dnsmasq_pid_file = f"/tmp/{self.net_name}-dnsmasq.pid"
        self.dnsmasq_conf_file = f"/tmp/{self.net_name}-dnsmasq.conf"
    
    def open(self) -> None:
        self.__start_dhcp__()

    def close(self):
        self.__stop_dhcp__()

    def __exec_ns__(self, cmd: list[str], check: bool = True) -> list[str]:
        return run(["ip", "netns", "exec", f"{self.net_name}"] + cmd, check)

    def __configure_dhcp__(self):
        dnsmasq_config: str = f"""
            interface={self.net_if}
            bind-interfaces
            dhcp-range={self.dhcp_begin},{self.dhcp_end},{self.dhcp_ttl}
            dhcp-option=3
            port=0
            log-dhcp
            log-debug
            log-queries
            leasefile-ro
            pid-file={self.dnsmasq_pid_file}
        """

        with open(self.dnsmasq_conf_file, "w") as f:
            f.write(dnsmasq_config)

        self.__exec_ns__(["ip", "address", "add", f"{self.ip_addr}/{self.net_pre_len}", "dev", f"{self.net_if}"])
    
    def __start_dhcp__(self):
        sys_install(dhcp_server_dependecies)
        self.__configure_dhcp__()
        print(f"Running dhcp on {self.net_if}.")
        self.__exec_ns__([ "dnsmasq", f"--conf-file={self.dnsmasq_conf_file}" ]) # "--keep-in-foreground",

    def __stop_dhcp__(self):
        try:
            if os.path.exists(self.dnsmasq_pid_file):
                with open(self.dnsmasq_pid_file) as f:
                    pid = int(f.read().strip())
                    os.kill(pid, signal.SIGTERM)
        except Exception:
            print("Stopping dhcp: wasnt found running.")

        if os.path.exists(self.dnsmasq_conf_file):
            os.remove(self.dnsmasq_conf_file)

class StaticClient():
    def __init__(self,
                 net_interface: str,
                 net_ip_addr: IPAddr,
                 net_prefix_len: int = 24) -> None:
        self.net_if: str = net_interface
        self.ip_addr: IPAddr = net_ip_addr
        self.net_pre_len: int = net_prefix_len
        self.__assign_static_ip__()

    def get_ip(self) -> IPAddr:
        if not sys_if_ip_addr(self.net_if):
            self.__assign_static_ip__()
        return cast(IPAddr, sys_if_ip_addr(self.net_if))
    
    def __assign_static_ip__(self) -> None:
        print("\nAssigning static IP addr...\n")
        run(["ip", "address", "add", f"{self.ip_addr}/{self.net_pre_len}", "dev", f"{self.net_if}"])

class DHCPClient():

    def __init__(self,
                 net_interface: str = "eth0") -> None:
        sys_install(network_client_dependecies)
        self.net_if = net_interface
        self.__request_dhcp_lease__()

    def get_ip(self) -> IPAddr:
        if not sys_if_ip_addr(self.net_if):
            self.__request_dhcp_lease__()
        return cast(IPAddr, sys_if_ip_addr(self.net_if))

    def __request_dhcp_lease__(self) -> None:
        print("\nRequesting DHCP lease...\n")
        run_unsafe(["dhclient", "-r", self.net_if], check=False)
        cache_file: str = f"/tmp/dhclient-{self.net_if}.leases"
        if sys_file_exists(cache_file):
            run(["rm", "-rf", cache_file])
        run([
            "dhclient", "-4", "-v",
            "-lf", cache_file,   # temporary lease cache -> avoid persistence
            "-pf", f"/tmp/dhclient-{self.net_if}.pid",      # same for pid
            self.net_if
        ])